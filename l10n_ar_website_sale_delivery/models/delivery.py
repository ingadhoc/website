##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, api, fields
import odoo.addons.decimal_precision as dp


class DeliveryCarrier(models.Model):

    _inherit = 'delivery.carrier'

    report_fixed_price = fields.Float(
        compute='compute_report_fixed_price',
        string='Taxed Price',
        digits=dp.get_precision('Account'),
    )

    @api.depends()
    def compute_report_fixed_price(self):
        # Get company
        website_id = self._context.get('website_id', False)
        if website_id:
            company_id = self.env['website'].browse(website_id).company_id.id
        else:
            company_id = self._context.get(
                'company_id', self.env.user.company_id.id)
        company = self.env['res.company'].browse(company_id)

        # Get parter
        user_id = self._context.get('uid', self.env.user.id)
        partner = self.env['res.users'].browse(user_id).partner_id

        taxes_included = not partner._get_vat_discriminated(partner, company)
        res_type = 'total_included' if taxes_included else 'total_excluded'
        for carrier in self:
            carrier.report_fixed_price = carrier.product_id.taxes_id.filtered(
                lambda x: x.company_id.id == company_id).compute_all(
                    carrier.fixed_price, product=carrier.product_id)[res_type]
