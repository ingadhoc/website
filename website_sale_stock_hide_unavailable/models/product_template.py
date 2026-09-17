from odoo import api, fields, models

# Stored template columns whose change can flip candidacy or availability.
RECOMPUTE_TRIGGER_FIELDS = {
    "allow_out_of_stock_order",
    "is_storable",
    "is_published",
    "attribute_line_ids",
}


class ProductTemplate(models.Model):
    _inherit = "product.template"

    # bypass_search_access: the 'not any' filter in website.sale_product_domain
    # must resolve for public/portal shoppers without granting them read access
    # to this internal table (which would leak per-warehouse stock over RPC).
    stock_unavailability_ids = fields.One2many(
        "product.template.stock.availability",
        "product_tmpl_id",
        bypass_search_access=True,
    )

    def write(self, vals):
        res = super().write(vals)
        if RECOMPUTE_TRIGGER_FIELDS & vals.keys():
            self.sudo()._enqueue_stock_availability()
        return res

    def _enqueue_stock_availability(self):
        if not self:
            return
        self.env["product.template.stock.dirty"].sudo().create([{"product_tmpl_id": tmpl_id} for tmpl_id in self.ids])

    def _hide_unavailable_is_candidate(self):
        """Only these products can be hidden or pushed down.

        The variant check lives here (not in the SQL enqueue) because
        product_variant_count is a non-stored compute.
        """
        self.ensure_one()
        return (
            self.is_storable
            and not self.allow_out_of_stock_order
            and self.is_published
            and self.product_variant_count == 1
        )

    @api.model
    def _hide_unavailable_candidate_domain(self):
        # Coarse gate on stored columns; the variant filter is applied afterwards.
        return [
            ("is_storable", "=", True),
            ("allow_out_of_stock_order", "=", False),
            ("is_published", "=", True),
        ]

    @api.model
    def _enqueue_all_candidates(self):
        candidates = self.search(self._hide_unavailable_candidate_domain())
        candidates._enqueue_stock_availability()
