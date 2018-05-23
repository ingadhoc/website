##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields, api
from odoo.http import request


class Website(models.Model):
    _inherit = 'website'

    sale_order_type_id = fields.Many2one(
        'sale.order.type',
        string='Sale Order Type',
    )

    @api.multi
    def _prepare_sale_order_values(self, partner, pricelist):
        res = super(Website, self)._prepare_sale_order_values(
            partner=partner, pricelist=pricelist)
        if partner.sale_type:
            res['type_id'] = partner.sale_type.id
        elif request.website.sale_order_type_id:
            res['type_id'] = request.website.sale_order_type_id.id
        return res
