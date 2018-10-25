##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, api, fields
import odoo.addons.decimal_precision as dp


class DeliveryCarrier(models.Model):

    _inherit = 'delivery.carrier'

    report_fixed_price = fields.Float(
        compute='_compute_report_fixed_price',
        string='Taxed Price',
        digits=dp.get_precision('Account'),
    )

    @api.depends()
    def _compute_report_fixed_price(self):
        company, partner = self.env['res.partner'].get_company_partner()
        taxes_included = not partner._get_vat_discriminated(partner, company)
        res_type = 'total_included' if taxes_included else 'total_excluded'
        for carrier in self:
            carrier.report_fixed_price = carrier.product_id.taxes_id.filtered(
                lambda x: x.company_id == company).compute_all(
                    carrier.fixed_price, product=carrier.product_id)[res_type]
