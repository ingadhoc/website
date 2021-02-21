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
        # If the line product pack has discount, non update prices fot this line.
        pack_line_with_discount = sale_order_line.pack_parent_line_id and \
            sale_order_line.pack_parent_line_id.product_id.pack_line_ids.filtered(
                lambda x: x.product_id == sale_order_line.product_id and x.sale_discount)
        if sale_order_line.pack_parent_line_id and not \
           sale_order_line.pack_parent_line_id.product_id.pack_modifiable or pack_line_with_discount:
            quantity = sale_order_line.product_uom_qty
            if sale_order_line.pack_parent_line_id.product_id.pack_modifiable:
                if set_qty:
                    quantity = set_qty
                elif add_qty is not None:
                    quantity += (add_qty or 0)
            return {'line_id': line_id, 'quantity': quantity}
        # we force to remove the packs lines when the partent line is removed from the order.
        if not self._context.get('update_pricelist', False) and set_qty == 0 and sale_order_line.pack_child_line_ids:
            sale_order_line.pack_child_line_ids.unlink()
        return super()._cart_update(
            product_id=product_id, line_id=line_id,
            add_qty=add_qty, set_qty=set_qty, **kwargs)
