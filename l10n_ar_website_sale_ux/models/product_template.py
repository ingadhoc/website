from odoo import models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def _get_sales_prices(self, pricelist):
        """ RG 4/2025 force us to show both prices in the e-commerce, with taxes and without taxes.
        If we have configured a tax included website then we compute the price_tax_excluded to be shown.
        (this is shown in the shop page table (list/grid view) """
        template_price_vals = super()._get_sales_prices(pricelist)
        if self.user_has_groups('account.group_show_line_subtotals_tax_included'):
            partner_sudo = self.env.user.partner_id
            fpos_id = self.env['website']._get_current_fiscal_position_id(partner_sudo)
            fiscal_position = self.env['account.fiscal.position'].sudo().browse(fpos_id)

            for product_tmpl_id, template_price_val in template_price_vals.items():
                template = self.env['product.template'].browse(product_tmpl_id)
                product_taxes = template.sudo().taxes_id.filtered(lambda t: t.company_id == t.env.company)
                taxes = fiscal_position.map_tax(product_taxes)
                template_price_vals[product_tmpl_id].update({'price_tax_excluded': taxes.with_context(force_price_include=True).compute_all(
                                    price_unit=template_price_val['price_reduce'],
                                    currency=pricelist.currency_id,
                                    quantity=1,
                                    product=template.sudo(),
                                    partner=partner_sudo,
                                )['total_excluded']})
        return template_price_vals

    def _get_combination_info(self, combination=False, product_id=False, add_qty=1, pricelist=False, parent_combination=False, only_template=False):
        """ RG 4/2025 force us to show both prices in the e-commerce, with taxes and without taxes.
        If we have configured a tax included website then we compute the price_tax_excluded to be shown.
        (this is shown in the product page view) """
        combination_info = super(ProductTemplate, self)._get_combination_info(
            combination=combination, product_id=product_id, add_qty=add_qty, pricelist=pricelist,
            parent_combination=parent_combination, only_template=only_template)
        combination_info.update({'price_tax_excluded':0})

        if self.env.context.get('website_id') and self.user_has_groups('account.group_show_line_subtotals_tax_included'):
            current_website = self.env['website'].get_current_website()
            if current_website and current_website.company_id.country_code == 'AR':
                if not pricelist:
                    pricelist = current_website.get_current_pricelist()
                company_id = current_website.company_id
                partner = self.env.user.partner_id
                product = self.env['product.product'].browse(combination_info['product_id']) or self
                fpos_id = self.env['website'].sudo()._get_current_fiscal_position_id(partner)
                fiscal_position = self.env['account.fiscal.position'].sudo().browse(fpos_id)
                product_taxes = product.sudo().taxes_id.filtered(lambda x: x.company_id == company_id)
                taxes = fiscal_position.map_tax(product_taxes)

                combination_info.update({'price_tax_excluded': taxes.with_context(
                    force_price_include=True).compute_all(
                        price_unit=combination_info['price'],
                        currency=pricelist.currency_id,
                        quantity=1,
                        product=product.sudo(),
                        partner=partner,
                    )['total_excluded']})

        return combination_info
