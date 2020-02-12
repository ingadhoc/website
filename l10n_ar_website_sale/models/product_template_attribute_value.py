##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import api, fields, models


class ProductTemplateAttributeValue(models.Model):

    _inherit = "product.template.attribute.value"

    report_price_extra = fields.Float(
        compute='_compute_report_price_extra')

    @api.depends()
    def _compute_report_price_extra(self):
        company, partner = self.env['res.partner'].get_company_partner()
        taxes_included = not partner._get_vat_discriminated(partner, company)
        ret = 'total_included' if taxes_included else 'total_excluded'

        if taxes_included:
            pricelist = self.env['product.pricelist'].browse(self._context.get('pricelist'))
            for rec in self:
                taxes = partner.property_account_position_id.map_tax(
                    rec.product_tmpl_id.sudo().taxes_id.filtered(
                        lambda x: x.company_id == company))
                rec.report_price_extra = taxes.sudo().compute_all(
                    rec.price_extra, pricelist.currency_id)[ret]
        else:
            for rec in self:
                rec.report_price_extra = rec.price_extra
