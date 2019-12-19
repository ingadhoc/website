##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################

from odoo import api, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.multi
    def _cart_update(
        self, product_id=None,
            line_id=None, add_qty=0, set_qty=0, **kwargs):
        sale_order_line = self.env['sale.order.line'].browse(line_id)
        if sale_order_line.pack_parent_line_id and not \
           sale_order_line.pack_parent_line_id.product_id.pack_modifiable \
           == 'frontend_backend':
            return {
                'line_id': line_id,
                'quantity': sale_order_line.product_uom_qty}
        return super()._cart_update(
            product_id=product_id, line_id=line_id,
            add_qty=add_qty, set_qty=set_qty, **kwargs)
