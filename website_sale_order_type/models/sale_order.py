# -*- encoding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################

from openerp import api, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    @api.onchange('partner_id')
    def onchange_partner_id(self):
        res = super(SaleOrder, self).onchange_partner_id()
        website_id = self._context.get('website_id', False)
        if website_id:
            sale_order_type = self.env['website'].browse(
                website_id).sale_order_type_id
            if sale_order_type:
                self.type_id = sale_order_type
        return res
