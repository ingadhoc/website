##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields


class Website(models.Model):
    _inherit = 'website'

    sale_order_type_id = fields.Many2one(
        'sale.order.type',
        string='Sale Order Type',
    )

    def _prepare_sale_order_values(self, partner, pricelist):
        res = super(Website, self)._prepare_sale_order_values(
            partner=partner, pricelist=pricelist)
        sale_type = (
            partner.sale_type or self.sale_order_type_id)

        if sale_type:
            res['type_id'] = sale_type.id
            if sale_type.warehouse_id:
                res['warehouse_id'] = sale_type.warehouse_id.id
                res['company_id'] = sale_type.warehouse_id.company_id.id
        return res
