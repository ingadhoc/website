# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, fields, api


class Website(models.Model):
    _inherit = 'website'

    sale_order_type_id = fields.Many2one(
        'sale.order.type',
        string='Sale Order Type',
    )

    @api.model
    def _prepare_sale_order_values(self, w, partner, pricelist):
        res = super(Website, self)._prepare_sale_order_values(
            w=w, partner=partner, pricelist=pricelist)
        if partner.sale_type:
            res['type_id'] = partner.sale_type.id
        elif w.sale_order_type_id:
            res['type_id'] = w.sale_order_type_id.id
        return res
