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

    def _prepare_sale_order_values(self, partner_sudo):
        res = super()._prepare_sale_order_values(partner_sudo=partner_sudo)
        sale_type = (partner_sudo.sale_type or self.sudo().sale_order_type_id)

        if sale_type:
            res['type_id'] = sale_type.id
            if sale_type.warehouse_id:
                res['warehouse_id'] = sale_type.warehouse_id.id
                res['company_id'] = sale_type.warehouse_id.company_id.id
        return res
