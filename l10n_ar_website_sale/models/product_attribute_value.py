##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import api, fields, models


class ProductAttributeValue(models.Model):

    _inherit = 'product.attribute.value'

    report_price_extra = fields.Float(
        'Attribute Price Extra',
        compute='_compute_report_price_extra')

    @api.depends()
    def _compute_report_price_extra(self):
        """
        """
        product_tmpl_id = self._context.get('active_id', False)
        if not product_tmpl_id:
            return
        product_tmpl = self.env['product.template'].browse(product_tmpl_id)
        company, partner = self.env['res.partner'].get_company_partner()
        pricelist = self.env['product.pricelist'].browse(
            self._context.get('pricelist'))

        taxes_included = not partner._get_vat_discriminated(partner, company)
        ret = 'total_included' if taxes_included else 'total_excluded'
        if taxes_included:
            for rec in self:
                taxes = partner.property_account_position_id.map_tax(
                    product_tmpl.sudo().taxes_id.filtered(
                        lambda x: x.company_id == company))
                rec.report_price_extra = taxes.sudo().compute_all(
                    rec.price_extra, pricelist.currency_id)[ret]
        else:
            for rec in self:
                rec.report_price_extra = rec.price_extra
