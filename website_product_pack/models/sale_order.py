##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################

from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _cart_update(
        self, product_id=None,
            line_id=None, add_qty=0, set_qty=0, **kwargs):
        sale_order_line = self.env['sale.order.line'].browse(line_id)
        if sale_order_line.pack_parent_line_id and not \
           sale_order_line.pack_parent_line_id.product_id.pack_modifiable:
            return {
                'line_id': line_id,
                'quantity': sale_order_line.product_uom_qty}
        # we force to remove the packs lines when the partent line is removed from the order.
        if set_qty == 0 and sale_order_line.pack_child_line_ids:
            sale_order_line.pack_child_line_ids.unlink()
        return super()._cart_update(
            product_id=product_id, line_id=line_id,
            add_qty=add_qty, set_qty=set_qty, **kwargs)
