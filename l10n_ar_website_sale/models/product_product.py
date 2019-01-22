##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
# flake8: noqa
# pylint: disable=pointless-string-statement
from odoo import models
from odoo.tools import float_compare, pycompat
from odoo.http import request


class ProductProduct(models.Model):

    _inherit = 'product.product'

    # NOTE this a copy of original odoo code that was added and edited here
    # because it was not able to inherit in other way.
    def _website_price(self):
        super(ProductProduct, self)._website_price()

        qty = self._context.get('quantity', 1.0)
        # ODOO ORIGINAL CODE COMMENTED
        """
        partner = self.env.user.partner_id
        """
        # THIS IS THE NEW CHANGE
        partner = request.env.user.partner_id.commercial_partner_id
        # END OF NEW CHANGE

        current_website = self.env['website'].get_current_website()
        pricelist = current_website.get_current_pricelist()
        company_id = current_website.company_id

        context = dict(self._context, pricelist=pricelist.id, partner=partner)
        self2 = self.with_context(context) if self._context != context else self

        # ODOO ORIGINAL CODE COMMENTED
        """
        ret = self.env.user.has_group('sale.group_show_price_subtotal') and  'total_excluded' or 'total_included'
        """
        # THIS IS THE NEW CHANGE
        # company_id, partner = partner.get_company_partner()
        taxes_included = not partner._get_vat_discriminated(
            partner, company_id)
        ret = 'total_included' if taxes_included else 'total_excluded'
        # END OF NEW CHANGE

        for p, p2 in pycompat.izip(self, self2):
            taxes = partner.property_account_position_id.map_tax(p.sudo().taxes_id.filtered(lambda x: x.company_id == company_id))
            p.website_price = taxes.compute_all(p2.price, pricelist.currency_id, quantity=qty, product=p2, partner=partner)[ret]
            # We must convert the price_without_pricelist in the same currency than the
            # website_price, otherwise the comparison doesn't make sense. Moreover, we show a price
            # difference only if the website price is lower
            price_without_pricelist = p.list_price
            if company_id.currency_id != pricelist.currency_id:
                price_without_pricelist = company_id.currency_id.compute(price_without_pricelist, pricelist.currency_id)
            price_without_pricelist = taxes.compute_all(price_without_pricelist, pricelist.currency_id)[ret]
            p.website_price_difference = True if float_compare(price_without_pricelist, p.website_price, precision_rounding=pricelist.currency_id.rounding) > 0 else False
            p.website_public_price = taxes.compute_all(p2.lst_price, quantity=qty, product=p2, partner=partner)[ret]
