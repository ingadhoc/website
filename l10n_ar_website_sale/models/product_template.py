from odoo import models, fields
from odoo.http import request

# flake8: noqa
# pylint: disable=pointless-string-statement


class ProductTemplate(models.Model):

    _inherit = 'product.template'

    vat_tax_id = fields.Many2one(
        'account.tax',
        compute='_compute_vat_tax_id',
    )

    def _compute_vat_tax_id(self):
        current_website = self.env['website'].get_current_website()
        company_id = current_website.company_id
        for rec in self:
            vat_taxes = rec.taxes_id.filtered(lambda x: (
                x.tax_group_id.type == 'tax' and
                x.tax_group_id.tax == 'vat' and x.company_id == company_id))
            rec.vat_tax_id = vat_taxes and vat_taxes[0].id

    # NOTE this a copy of original odoo code that was added and edited here because it was not able to inherit in other way.
    def _get_combination_info(self, combination=False, product_id=False, add_qty=1, pricelist=False, parent_combination=False, only_template=False):
        """Override for website, where we want to:
            - take the website pricelist if no pricelist is set
            - apply the b2b/b2c setting to the result

        This will work when adding website_id to the context, which is done
        automatically when called from routes with website=True.
        """
        self.ensure_one()

        current_website = False

        if self.env.context.get('website_id'):
            current_website = self.env['website'].get_current_website()
            if not pricelist:
                pricelist = current_website.get_current_pricelist()

        combination_info = super(ProductTemplate, self)._get_combination_info(
            combination=combination, product_id=product_id, add_qty=add_qty, pricelist=pricelist,
            parent_combination=parent_combination, only_template=only_template)

        if self.env.context.get('website_id'):
            # THIS IS THE NEW CHANGE
            partner = request.env.user.partner_id.commercial_partner_id
            # ODOO ORIGINAL CODE COMMENTED
            """
            partner = self.env.user.partner_id
            """
            company_id = current_website.company_id
            product = self.env['product.product'].browse(combination_info['product_id']) or self

            # THIS IS THE NEW CHANGE
            # company_id, partner = partner.get_company_partner()
            taxes_included = not partner._get_vat_discriminated(partner, company_id)
            tax_display = 'total_included' if taxes_included else 'total_excluded'
            # ODOO ORIGINAL CODE COMMENTED
            """
            tax_display = self.env.user.has_group('account.group_show_line_subtotals_tax_excluded') and 'total_excluded' or 'total_included'
            """
            taxes = partner.property_account_position_id.map_tax(product.sudo().taxes_id.filtered(lambda x: x.company_id == company_id), product, partner)

            # The list_price is always the price of one.
            quantity_1 = 1
            price = taxes.compute_all(combination_info['price'], pricelist.currency_id, quantity_1, product, partner)[tax_display]
            if pricelist.discount_policy == 'without_discount':
                list_price = taxes.compute_all(combination_info['list_price'], pricelist.currency_id, quantity_1, product, partner)[tax_display]
            else:
                list_price = price
            has_discounted_price = pricelist.currency_id.compare_amounts(list_price, price) == 1

            combination_info.update(
                price=price,
                list_price=list_price,
                has_discounted_price=has_discounted_price,
            )

        return combination_info
