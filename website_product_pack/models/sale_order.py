# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################

from openerp import api, models
from openerp import SUPERUSER_ID


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.multi
    def _cart_update(
        self, product_id=None,
            line_id=None, add_qty=0, set_qty=0, **kwargs):
        sale_order_line = self.env['sale.order.line'].browse(line_id)
        if sale_order_line.pack_parent_line_id:
            return {
                'line_id': line_id,
                'quantity': sale_order_line.product_uom_qty}
        return super(SaleOrder, self)._cart_update(
            product_id=product_id, line_id=line_id,
            add_qty=add_qty, set_qty=set_qty, **kwargs)

    def _cart_find_product_line(
            self, cr, uid, ids,
            product_id=None, line_id=None, context=None, **kwargs):
        # la funcion no es muy heredable, podriamos agarrar estos resultados
        # y buscar sobre ellos pero esto haria que se ejecuten dos sql
        # line_ids = super(SaleOrder, self)._cart_find_product_line(
        #     cr, uid, ids, product_id=product_id, line_id=line_id,
        #     context=context, **kwargs)
        for so in self.browse(cr, uid, ids, context=context):
            domain = [('order_id', '=', so.id),
                      ('product_id', '=', product_id),
                      ('pack_parent_line_id', '=', False)]
            if line_id:
                domain += [('id', '=', line_id)]
            return self.pool.get('sale.order.line').search(
                cr, SUPERUSER_ID, domain, context=context)
