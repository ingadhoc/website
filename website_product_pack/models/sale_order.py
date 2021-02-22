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
            return {'line_id': line_id, 'quantity': sale_order_line.product_uom_qty}
        # we force to remove the packs lines when the partent line is removed from the order.
        if not self._context.get('update_pricelist', False) and set_qty == 0 and sale_order_line.pack_child_line_ids:
            sale_order_line.pack_child_line_ids.unlink()
        return super()._cart_update(
            product_id=product_id, line_id=line_id,
            add_qty=add_qty, set_qty=set_qty, **kwargs)

    def _website_product_id_change(self, order_id, product_id, qty=0):
        order = self.sudo().browse(order_id)
        product = self.env['product.product'].browse(product_id)
        sale_order_line = order.order_line.filtered(lambda x: x.product_id == product and x.pack_parent_line_id)
        pack_line_with_discount = sale_order_line and sale_order_line[0].pack_parent_line_id.product_id.pack_line_ids.filtered(
            lambda x: x.product_id == product and x.sale_discount)

        # If the line product pack has discount, non update prices for this line.
        if pack_line_with_discount:
            return {
                'product_id': product_id,
                'product_uom_qty': qty,
                'order_id': order_id,
                'product_uom': product.uom_id.id,
                'price_unit': sale_order_line[0].price_unit,
                'discount': sale_order_line[0].discount,
            }
        return super()._website_product_id_change(order_id, product_id, qty=qty)
