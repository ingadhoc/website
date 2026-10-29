from odoo import models

# Stored variant columns whose change can flip the template's availability.
RECOMPUTE_TRIGGER_FIELDS = {"active"}


class ProductProduct(models.Model):
    _inherit = "product.product"

    def write(self, vals):
        res = super().write(vals)
        if RECOMPUTE_TRIGGER_FIELDS & vals.keys():
            # Availability is read over every variant, so archiving the only one
            # with stock leaves the template unavailable, and the reverse.
            # Candidates are recomputed; the rest only to clear rows they still
            # have, which keeps a mass archive from flooding the queue.
            templates = self.sudo().product_tmpl_id
            templates.filtered(
                lambda tmpl: tmpl._hide_unavailable_is_candidate() or tmpl.stock_unavailability_ids
            )._enqueue_stock_availability()
        return res
