from odoo import models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _should_show_strikethrough_price(self):
        # Cart / order summary lines render the strikethrough from this hook. Hide
        # it when the order's pricelist requests it.
        if self.order_id.pricelist_id.website_hide_strikethrough_price:
            return False
        return super()._should_show_strikethrough_price()
