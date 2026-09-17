from odoo import api, fields, models
from odoo.fields import Domain

DRAIN_BATCH = 500
SWEEP_BATCH = 2000


class Website(models.Model):
    _inherit = "website"

    out_of_stock_display = fields.Selection(
        [
            ("show", "Show"),
            ("last", "Show at the end of the list"),
            ("hide", "Hide"),
        ],
        string="Out-of-stock products",
        default="show",
        required=True,
        help="What the shop does with storable products that are out of stock "
        "and cannot be sold out of stock. 'Show' keeps Odoo's standard "
        "behaviour.",
    )

    # -- Frontend -----------------------------------------------------------

    def sale_product_domain(self):
        domain = super().sale_product_domain()
        website = self or self.get_current_website()
        if website.out_of_stock_display != "hide":
            return domain
        # 'not any' compiles to a SQL sub-query (not an "id in (...)"), so the
        # single override also covers the category product count.
        return domain & Domain("stock_unavailability_ids", "not any", website._hide_unavailable_scope_leaf())

    def _hide_unavailable_scope_leaf(self):
        """Leaf matching the unavailability rows of this website's scope.

        warehouse_id is False when the website has no warehouse set, which maps
        to the company-wide rows. Seam a multi-warehouse bridge overrides.
        """
        self.ensure_one()
        return [
            ("warehouse_id", "=", self.warehouse_id.id),
            ("company_id", "=", self.company_id.id),
        ]

    def _get_unavailable_tmpl_ids(self, templates):
        self.ensure_one()
        if self.out_of_stock_display not in ("hide", "last") or not templates:
            return set()
        # sudo: internal optimisation table, read from the public shop controller.
        rows = (
            self.env["product.template.stock.availability"]
            .sudo()
            .search(
                [
                    ("product_tmpl_id", "in", templates.ids),
                    ("warehouse_id", "=", self.warehouse_id.id),
                    ("company_id", "=", self.company_id.id),
                ]
            )
        )
        return set(rows.product_tmpl_id.ids)

    # -- Config changes -----------------------------------------------------

    def write(self, vals):
        res = super().write(vals)
        if {"warehouse_id", "company_id", "out_of_stock_display"} & vals.keys():
            self.env["product.template"].sudo()._enqueue_all_candidates()
        return res

    # -- Backend recompute --------------------------------------------------

    @api.model
    def _hide_unavailable_active_scopes(self):
        """Scopes the shop actually uses: {(warehouse_id | False, company_id)}."""
        websites = self.search([("out_of_stock_display", "in", ("hide", "last"))])
        return {(w.warehouse_id.id or False, w.company_id.id) for w in websites}

    @api.model
    def _hide_unavailable_free_qty(self, variants, warehouse_id, company_id):
        """Available quantity per variant for a scope.

        Mirrors what the storefront reads: free_qty with the warehouse in
        context (False = whole company), resolved in the scope's company so the
        blank-warehouse case sums the right warehouses. Reuses the standard
        batched compute (mrp kits, expiry... included). Seam a multi-warehouse
        bridge overrides.
        """
        variants = variants.with_context(
            warehouse_id=warehouse_id or False,
            allowed_company_ids=[company_id],
        )
        return {variant.id: variant.free_qty for variant in variants}

    @api.model
    def _recompute_stock_availability(self, templates):
        """Reconcile the unavailability rows of ``templates`` for every scope."""
        Availability = self.env["product.template.stock.availability"]
        templates = templates.exists()
        if not templates:
            return

        candidates = templates.filtered(lambda t: t._hide_unavailable_is_candidate())
        non_candidates = templates - candidates
        if non_candidates:
            # A product that gained variants or became sellable must reappear.
            Availability.search([("product_tmpl_id", "in", non_candidates.ids)]).unlink()
        if not candidates:
            return

        active = self._hide_unavailable_active_scopes()
        existing = Availability.search([("product_tmpl_id", "in", candidates.ids)])
        existing_by_key = {(r.product_tmpl_id.id, r.warehouse_id.id or False, r.company_id.id): r for r in existing}
        wanted = set()
        to_create = []
        for warehouse_id, company_id in active:
            scope_templates = candidates.filtered(lambda t, c=company_id: not t.company_id or t.company_id.id == c)
            if not scope_templates:
                continue
            free_qty = self._hide_unavailable_free_qty(scope_templates.product_variant_id, warehouse_id, company_id)
            for tmpl in scope_templates:
                if free_qty.get(tmpl.product_variant_id.id, 0.0) > 0:
                    continue
                key = (tmpl.id, warehouse_id or False, company_id)
                wanted.add(key)
                if key not in existing_by_key:
                    to_create.append(
                        {
                            "product_tmpl_id": tmpl.id,
                            "warehouse_id": warehouse_id or False,
                            "company_id": company_id,
                        }
                    )

        stale = Availability.browse(
            [row.id for key, row in existing_by_key.items() if (key[1], key[2]) in active and key not in wanted]
        )
        if stale:
            stale.unlink()
        if to_create:
            Availability.create(to_create)

    # -- Crons --------------------------------------------------------------

    @api.model
    def _cron_drain_stock_availability(self, batch=DRAIN_BATCH):
        Dirty = self.env["product.template.stock.dirty"]
        rows = Dirty.search([], limit=batch)
        if not rows:
            return
        self._recompute_stock_availability(rows.product_tmpl_id)
        rows.unlink()

    @api.model
    def _cron_full_sweep_stock_availability(self, batch=SWEEP_BATCH):
        Availability = self.env["product.template.stock.availability"]
        active = self._hide_unavailable_active_scopes()
        orphans = Availability.search([]).filtered(
            lambda r: (r.warehouse_id.id or False, r.company_id.id) not in active
        )
        if orphans:
            orphans.unlink()
        Template = self.env["product.template"]
        candidates = Template.search(Template._hide_unavailable_candidate_domain())
        Cron = self.env["ir.cron"]
        remaining = len(candidates)
        for index in range(0, len(candidates), batch):
            chunk = candidates[index : index + batch]
            self._recompute_stock_availability(chunk)
            remaining -= len(chunk)
            # Commit each batch: a large catalogue neither runs in one long
            # transaction nor is left partially reconciled if the cron is cut
            # off (outside a cron run this call just commits).
            Cron._commit_progress(len(chunk), remaining=remaining)
