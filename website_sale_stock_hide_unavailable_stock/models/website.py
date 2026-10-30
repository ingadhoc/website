from odoo import models


class Website(models.Model):
    _inherit = "website"

    def write(self, vals):
        res = super().write(vals)
        # The warehouse is what this website measures availability against, so
        # changing it changes every answer. The field comes from
        # website_sale_stock, which is why the trigger lives here.
        if "warehouse_id" in vals:
            self._trigger_stock_availability_sweep()
        return res
