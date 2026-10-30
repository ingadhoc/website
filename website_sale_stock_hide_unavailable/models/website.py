from odoo import api, fields, models
from odoo.fields import Domain
from odoo.tools import SQL

DRAIN_BATCH = 500
SWEEP_BATCH = 2000
SWEEP_CURSOR_PARAM = "website_sale_stock_hide_unavailable.sweep_cursor"
REPUBLISH_BATCH = 1000


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
        website = self or self.env.website
        if website.out_of_stock_display != "hide":
            return domain
        # 'not any' compiles to a SQL sub-query (not an "id in (...)"), so the
        # single override also covers the category product count.
        return domain & Domain("stock_unavailability_ids", "not any", website._hide_unavailable_scope_leaf())

    def _hide_unavailable_scope_leaf(self):
        """Leaf matching the unavailability rows of this website."""
        self.ensure_one()
        return [("website_id", "=", self.id)]

    def _get_unavailable_tmpl_ids(self, templates):
        self.ensure_one()
        if self.out_of_stock_display not in ("hide", "last") or not templates:
            return set()
        # Only the ids, in one query. The rows of a scope are few (just the
        # sold-out products), while filtering by product_tmpl_id would send the
        # whole catalogue as an IN list, because the shop lookup runs with
        # limit=None. Reading them as records would build the whole recordset on
        # every shop request only to intersect ids.
        Availability = self.env["product.template.stock.availability"]
        Availability.flush_model(["product_tmpl_id", "website_id"])
        self.env.cr.execute(
            SQL(
                """
                SELECT product_tmpl_id
                  FROM product_template_stock_availability
                 WHERE website_id = %s
                """,
                self.id,
            )
        )
        return {row[0] for row in self.env.cr.fetchall()} & set(templates.ids)

    # -- Config changes -----------------------------------------------------

    @api.model_create_multi
    def create(self, vals_list):
        websites = super().create(vals_list)
        if any(website.out_of_stock_display in ("hide", "last") for website in websites):
            websites._trigger_stock_availability_sweep()
        return websites

    def write(self, vals):
        res = super().write(vals)
        if {"company_id", "out_of_stock_display"} & vals.keys():
            self._trigger_stock_availability_sweep()
        return res

    @api.model
    def _hide_unavailable_take_over_native(self):
        """Take over the out-of-stock treatment from Odoo's own, at install.

        The native unpublishing stops running once its group is gone, so what it
        had already unpublished would stay unpublished for good. Those products
        are republished first: this module keeps them published and filters the
        listing instead, which is what keeps their page answering 200.
        """
        if self.env["res.groups"]._is_feature_enabled("website_sale.group_unpublish_out_of_stock"):
            self._republish_natively_unpublished()
        self._disable_native_unpublishing()

    @api.model
    def _republish_natively_unpublished(self):
        """Republish what the native unpublishing had taken down.

        Same signature it leaves behind, read from
        website_sale.product_template._compute_is_published: there is no marker
        of which products it took down, and while it was on, a sold-out one was
        going to be republished the moment it had stock again.

        Walked in batches: this runs inside the install transaction and the
        catalogue can be large.
        """
        Template = self.env["product.template"].sudo()
        domain = [
            ("is_published", "=", False),
            ("is_storable", "=", True),
            ("allow_out_of_stock_order", "=", False),
        ]
        last_id = 0
        while True:
            batch = Template.search(domain + [("id", ">", last_id)], limit=REPUBLISH_BATCH, order="id")
            if not batch:
                break
            last_id = max(batch.ids)
            sold_out = batch.filtered(lambda tmpl: all(v.free_qty <= 0 for v in tmpl.product_variant_ids))
            if sold_out:
                dates = [(tmpl.publish_date, tmpl.id) for tmpl in sold_out]
                sold_out.is_published = True
                sold_out.flush_recordset()
                # publish_date is a stored compute of is_published, so it moves
                # to now() and cannot be written back through the ORM. Letting
                # it move would send the whole backlog to the top of "Newest
                # Arrivals" and hand it the "New" ribbon.
                self.env.cr.executemany("UPDATE product_template SET publish_date = %s WHERE id = %s", dates)
            self.env.flush_all()
            self.env.invalidate_all()

    @api.model
    def _disable_native_unpublishing(self):
        """Turn off Odoo's own unpublishing, which this module replaces.

        Only when the module takes over, on install and on upgrade: the setting
        is not offered any more, so it must not stay on where nobody can see
        it. Nothing keeps checking afterwards -- Odoo's own settings page reads
        the group before saving and writes it back, so a module that undid it
        mid-save would only be undone in turn, and would break the native
        feature for whoever does turn it back on. Enabling the group over RPC
        is still possible: the README says so.
        """
        group = self.env.ref("website_sale.group_unpublish_out_of_stock", raise_if_not_found=False)
        editor = self.env.ref("website.group_website_restricted_editor", raise_if_not_found=False)
        if group and editor:
            editor.sudo()._remove_group(group.sudo())

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
    @api.ormcache()
    def _hide_unavailable_any_active_scope(self):
        """Whether any website does something with out-of-stock products.

        The module ships with the shop, so most databases leave every website on
        'show'. Asking first keeps them from paying for a feature they do not
        use: nothing is queued and the crons find an empty queue. Cached because
        every enqueue path asks and the answer changes a handful of times in the
        life of a database: out_of_stock_display is one of website's
        _clear_cache_on_fields, so the ORM drops this entry on its own when one
        is written, and on any create or unlink.
        """
        return bool(self.sudo().search_count([("out_of_stock_display", "in", ("hide", "last"))], limit=1))

    @api.model
    def _hide_unavailable_active_scopes(self):
        """The websites that actually do something with out-of-stock products."""
        return self.search([("out_of_stock_display", "in", ("hide", "last"))])

    def _hide_unavailable_free_qty(self, variants):
        """Available quantity per variant, as this website measures it.

        Asks the core seam: without Inventory it resolves to the company, and
        website_sale_stock overrides it to pass this website's warehouse. That
        is also what the storefront reads, so both answer the same.
        """
        self.ensure_one()
        variants = variants.with_context(allowed_company_ids=[self.company_id.id])
        return {variant.id: self._get_product_available_qty(variant) for variant in variants}

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
            # A product that became sellable or unpublished must reappear.
            Availability.search([("product_tmpl_id", "in", non_candidates.ids)]).unlink()
        if not candidates:
            return

        active = self._hide_unavailable_active_scopes()
        existing = Availability.search([("product_tmpl_id", "in", candidates.ids)])
        existing_by_key = {(r.product_tmpl_id.id, r.website_id.id): r for r in existing}
        wanted = set()
        to_create = []
        for website in active:
            company = website.company_id
            scope_templates = candidates.filtered(lambda t, c=company.id: not t.company_id or t.company_id.id == c)
            if not scope_templates:
                continue
            free_qty = website._hide_unavailable_free_qty(scope_templates.product_variant_ids)
            for tmpl in scope_templates:
                # Sold out only when every variant is, same rule as _is_sold_out().
                if any(free_qty.get(variant.id, 0.0) > 0 for variant in tmpl.product_variant_ids):
                    continue
                key = (tmpl.id, website.id)
                wanted.add(key)
                if key not in existing_by_key:
                    to_create.append({"product_tmpl_id": tmpl.id, "website_id": website.id})

        active_ids = set(active.ids)
        stale = Availability.browse(
            [row.id for key, row in existing_by_key.items() if key[1] in active_ids and key not in wanted]
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
        cursor = Param.get_int(SWEEP_CURSOR_PARAM, 0)
        active = self._hide_unavailable_active_scopes()
        if not cursor or not active:
            # Starting a pass, or nothing left to compute: drop the rows of the
            # scopes no website uses any more.
            # A domain, not search([]) + filtered: only the orphan rows are read.
            orphans = Availability.search([("website_id", "not in", active.ids)])
            if orphans:
                orphans.unlink()
        if not active:
            # Walking the whole catalogue for nobody would cost every database
            # with a shop a feature none of its websites turned on.
            Param.set_int(SWEEP_CURSOR_PARAM, 0)
            return
        domain = Template._hide_unavailable_candidate_domain()
        if in_cron:
            Cron._commit_progress(remaining=Template.search_count(domain + [("id", ">", cursor)]))
        while True:
            candidates = Template.search(domain + [("id", ">", cursor)], limit=batch, order="id")
            if not candidates:
                # Pass complete: the next run starts a fresh one.
                Param.set_int(SWEEP_CURSOR_PARAM, 0)
                if in_cron:
                    Cron._commit_progress(remaining=0)
                break
            self._recompute_stock_availability(candidates)
            cursor = max(candidates.ids)
            Param.set_int(SWEEP_CURSOR_PARAM, cursor)
            # Commit each batch and stop on time; the cron is then rescheduled
            # and resumes from the cursor instead of starting over.
            if in_cron and Cron._commit_progress(len(candidates)) <= 0:
                break
