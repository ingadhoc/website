from odoo import models

# Stored variant columns whose change can flip the template's availability.
# qty_available is a plain company-dependent column in `product`: without
# Inventory it is what the shop reads, and it can be typed by hand.
RECOMPUTE_TRIGGER_FIELDS = {"active", "qty_available"}


class ProductProduct(models.Model):
    _inherit = "product.product"

    def write(self, vals):
        res = super().write(vals)
        if RECOMPUTE_TRIGGER_FIELDS & vals.keys():
            # Availability is read over every variant, so archiving the only one
            # with stock leaves the template unavailable, and the reverse.
            self.sudo().product_tmpl_id._hide_unavailable_enqueue_candidates()
        return res
