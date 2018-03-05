# -*- coding: utf-8 -*-
from openerp import SUPERUSER_ID, models, api
# from openerp.osv import orm


class Website(models.Model):
    _inherit = 'website'

    @api.model
    def _prepare_sale_order_values(self, w, partner, pricelist):
        # backport from v11
        values = super(Website, self)._prepare_sale_order_values(
            w, partner, pricelist)
        if values['company_id']:
            warehouse_id = (
                self.env['ir.values'].get_default(
                    'sale.order', 'warehouse_id',
                    company_id=values.get('company_id')) or
                self.env['ir.values'].get_default(
                    'sale.order', 'warehouse_id') or
                self.env['stock.warehouse'].sudo().search(
                    [('company_id', '=', values['company_id'])], limit=1).id
            )
            if warehouse_id:
                values['warehouse_id'] = warehouse_id
        return values
