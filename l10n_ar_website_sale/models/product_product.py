from odoo import models, api
from odoo.tools import float_is_zero, pycompat

class ProductProduct(models.Model):

    _inherit = 'product.product'

    def _website_price(self):
        qty = self._context.get('quantity', 1.0)
        partner = self.env.user.partner_id
        current_website = self.env['website'].get_current_website()
        pricelist = current_website.get_current_pricelist()
        company_id = current_website.company_id
        context = dict(self._context, pricelist=pricelist.id, partner=partner)
        self2 = self.with_context(context) if self._context != context else self

        # Us
        company_id, partner = partner.get_company_partner()
        taxes_included = not partner._get_vat_discriminated(partner, company_id)
        ret = 'total_included' if taxes_included else 'total_excluded'
        # Odoo original code
        # ret = self.env.user.has_group('sale.group_show_price_subtotal') and 'total_excluded' or 'total_included'

        for p, p2 in pycompat.izip(self, self2):
            taxes = partner.property_account_position_id.map_tax(
                p.sudo().taxes_id.filtered(
                    lambda x: x.company_id == company_id))
            p.website_price = taxes.compute_all(
                p2.price, pricelist.currency_id, quantity=qty, product=p2,
                partner=partner)[ret]
            price_without_pricelist = taxes.compute_all(
                p.list_price, pricelist.currency_id)[ret]
            p.website_price_difference = False if float_is_zero(
                price_without_pricelist - p.website_price, precision_rounding=pricelist.currency_id.rounding) else True
            p.website_public_price = taxes.compute_all(
                p2.lst_price, quantity=qty, product=p2, partner=partner)[ret]
