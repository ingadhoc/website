##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _cart_update_order_line(self, product_id, quantity, order_line, **kwargs):
        order_line = super()._cart_update_order_line(product_id, quantity, order_line, **kwargs)
        if order_line:
            order_line._compute_discount()
            order_line.discount1 = order_line.discount
        return order_line
