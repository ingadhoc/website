##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################

from odoo import models, _


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _cart_update(self, product_id=None,line_id=None, add_qty=0, set_qty=0, **kwargs):
        sale_order_line = self.env['sale.order.line'].browse(line_id)
        if sale_order_line.pack_parent_line_id and not \
           sale_order_line.pack_parent_line_id.product_id.pack_modifiable:
            return {'line_id': line_id, 'quantity': sale_order_line.product_uom_qty}
        # we force to remove the packs lines when the partent line is removed from the order.
        if not self._context.get('update_pricelist', False) and set_qty == 0 and sale_order_line.pack_child_line_ids:
            sale_order_line.pack_child_line_ids.unlink()
        values = super()._cart_update(product_id, line_id, add_qty, set_qty, **kwargs)
        for line in self.order_line:
            if (line.product_id.type == 'product' or line.product_id.pack_ok == True) and line.product_id.inventory_availability in ['always', 'threshold']:
                cart_qty = sum(self.order_line.filtered(lambda p: p.product_id.id == line.product_id.id).mapped('product_uom_qty'))
                # The quantity should be computed based on the warehouse of the website, not the
                # warehouse of the SO.
                website = self.env['website'].get_current_website()
                if cart_qty > line.product_id.with_context(warehouse=website.warehouse_id.id).virtual_available and (line_id == line.id):
                    qty = line.product_id.with_context(warehouse=website.warehouse_id.id).virtual_available - cart_qty
                    new_val = super()._cart_update(line.product_id.id, line.id, qty, 0, **kwargs)
                    values.update(new_val)

                    # Make sure line still exists, it may have been deleted in super()_cartupdate because qty can be <= 0
                    if line.exists() and new_val['quantity']:
                        line.warning_stock = _('You ask for %s products but only %s is available') % (cart_qty, new_val['quantity'])
                        values['warning'] = line.warning_stock
                    else:
                        self.warning_stock = _("Some products became unavailable and your cart has been updated. We're sorry for the inconvenience.")
                        values['warning'] = self.warning_stock
        return values

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
