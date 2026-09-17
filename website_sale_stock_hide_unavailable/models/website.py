from odoo import api, fields, models
from odoo.fields import Domain

DRAIN_BATCH = 500
SWEEP_BATCH = 2000
SWEEP_CURSOR_PARAM = "website_sale_stock_hide_unavailable.sweep_cursor"


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
        # Read the unavailable rows of this scope and intersect in Python: they
        # are few (only sold-out products), while filtering by product_tmpl_id
        # would send the whole catalogue as an IN list, because the shop lookup
        # runs with limit=None.
        # sudo: internal optimisation table, read from the public shop controller.
        rows = (
            self.env["product.template.stock.availability"]
            .sudo()
            .search(
                [
                    ("warehouse_id", "=", self.warehouse_id.id),
                    ("company_id", "=", self.company_id.id),
                ]
            )
        )
        return set(rows.product_tmpl_id.ids) & set(templates.ids)

    # -- Config changes -----------------------------------------------------

    @api.model_create_multi
    def create(self, vals_list):
        websites = super().create(vals_list)
        if any(website.out_of_stock_display in ("hide", "last") for website in websites):
            websites._trigger_stock_availability_sweep()
        return websites

    def write(self, vals):
        res = super().write(vals)
        if {"warehouse_id", "company_id", "out_of_stock_display"} & vals.keys():
            self._trigger_stock_availability_sweep()
        return res

    def _trigger_stock_availability_sweep(self):
        """Ask the sweep to reconcile the catalogue, out of the request.

        Queueing one row per candidate here would block saving the Settings
        page on a large catalogue.
        """
        sweep = self.env.ref(
            "website_sale_stock_hide_unavailable.cron_full_sweep_stock_availability",
            raise_if_not_found=False,
        )
        if sweep:
            sweep.sudo()._trigger()

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
            # exists(): the other cron may have removed the same rows already.
            stale.exists().unlink()
        Availability._create_skip_conflicts(to_create)

    # -- Crons --------------------------------------------------------------

    @api.model
    def _hide_unavailable_in_cron(self):
        """Whether this runs as a cron job, so progress can be committed.

        Same signal the cron progress API itself looks at.
        """
        return bool(self.env.context.get("ir_cron_progress_id"))

    @api.model
    def _cron_drain_stock_availability(self, batch=DRAIN_BATCH):
        Dirty = self.env["product.template.stock.dirty"]
        Cron = self.env["ir.cron"]
        # Snapshot the head of the queue. Every row at or below it predates the
        # recomputes this run makes, so a single pass over a product clears all
        # of its queued rows at once instead of one row at a time. Rows queued
        # while the run is in flight get a higher id, survive, and are handled
        # by the next run, so no stock change is ever dropped.
        head = Dirty.search([], order="id desc", limit=1)
        if not head:
            return
        last_id = head.id
        remaining = Dirty.search_count([("id", "<=", last_id)])
        # _commit_progress always commits, and committing is forbidden inside a
        # test, so only report progress when actually running as a cron job.
        in_cron = self._hide_unavailable_in_cron()
        if in_cron:
            Cron._commit_progress(remaining=remaining)
        while True:
            rows = Dirty.search([("id", "<=", last_id)], limit=batch, order="id")
            if not rows:
                if in_cron:
                    Cron._commit_progress(remaining=0)
                break
            templates = rows.product_tmpl_id
            self._recompute_stock_availability(templates)
            done = Dirty.search([("product_tmpl_id", "in", templates.ids), ("id", "<=", last_id)])
            processed = len(done)
            done.unlink()
            if not processed:
                break
            remaining = max(remaining - processed, 0)
            # Commit each batch and stop when the cron runs out of time; it is
            # then rescheduled to continue with whatever is left in the queue.
            if in_cron and Cron._commit_progress(processed, remaining=remaining) <= 0:
                break

    @api.model
    def _cron_full_sweep_stock_availability(self, batch=SWEEP_BATCH):
        Availability = self.env["product.template.stock.availability"]
        Template = self.env["product.template"]
        Cron = self.env["ir.cron"]
        Param = self.env["ir.config_parameter"].sudo()
        in_cron = self._hide_unavailable_in_cron()
        # Resumable cursor over the candidates, ordered by id. Without it,
        # stopping on the time budget would restart from the first candidate on
        # every run and never reach the tail of a large catalogue.
        cursor = int(Param.get_param(SWEEP_CURSOR_PARAM, 0))
        if not cursor:
            # Starting a pass: drop the rows of scopes no website uses any more.
            active = self._hide_unavailable_active_scopes()
            orphans = Availability.search([]).filtered(
                lambda r: (r.warehouse_id.id or False, r.company_id.id) not in active
            )
            if orphans:
                orphans.unlink()
        domain = Template._hide_unavailable_candidate_domain()
        if in_cron:
            Cron._commit_progress(remaining=Template.search_count(domain + [("id", ">", cursor)]))
        while True:
            candidates = Template.search(domain + [("id", ">", cursor)], limit=batch, order="id")
            if not candidates:
                # Pass complete: the next run starts a fresh one.
                Param.set_param(SWEEP_CURSOR_PARAM, 0)
                if in_cron:
                    Cron._commit_progress(remaining=0)
                break
            self._recompute_stock_availability(candidates)
            cursor = max(candidates.ids)
            Param.set_param(SWEEP_CURSOR_PARAM, cursor)
            # Commit each batch and stop on time; the cron is then rescheduled
            # and resumes from the cursor instead of starting over.
            if in_cron and Cron._commit_progress(len(candidates)) <= 0:
                break
