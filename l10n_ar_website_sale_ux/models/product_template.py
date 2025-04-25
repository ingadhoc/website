from odoo import models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def _get_sales_prices(self, website):
        """RG 4/2025 force us to show both prices in the e-commerce, with taxes and without taxes.
        If we have configured a tax included website then we compute the price_tax_excluded to be shown.
        (this is shown in the shop page table (list/grid view)"""
        template_price_vals = super()._get_sales_prices(website)
        partner_sudo = self.env.user.partner_id
        for product_tmpl_id, template_price_val in template_price_vals.items():
            if (
                website
                and website.company_id.country_code == "AR"
                and website.show_line_subtotals_tax_selection == "tax_included"
            ):
                template = self.env["product.template"].browse(product_tmpl_id)
                fiscal_position = website.fiscal_position_id.sudo()
                product_taxes = template.sudo().taxes_id._filter_taxes_by_company(self.env.company)
                taxes = fiscal_position.map_tax(product_taxes)
                template_price_vals[product_tmpl_id].update(
                    {
                        "price_tax_excluded": taxes.with_context(force_price_include=True).compute_all(
                            price_unit=template_price_val["price_reduce"],
                            currency=website.currency_id,
                            quantity=1,
                            product=template.sudo(),
                            partner=partner_sudo,
                        )["total_excluded"]
                    }
                )
            else:
                template_price_vals[product_tmpl_id].update({"price_tax_excluded": 0})

        return template_price_vals

    def _get_additionnal_combination_info(self, product_or_template, quantity, date, website):
        combination_info = super()._get_additionnal_combination_info(product_or_template, quantity, date, website)
        if (
            website
            and website.company_id.country_code == "AR"
            and website.show_line_subtotals_tax_selection == "tax_included"
        ):
            partner = self.env.user.partner_id
            product_taxes = product_or_template.sudo().taxes_id._filter_taxes_by_company(website.company_id)
            taxes = website.fiscal_position_id.map_tax(product_taxes)

            combination_info.update(
                {
                    "price_tax_excluded": taxes.with_context(force_price_include=True).compute_all(
                        price_unit=combination_info["price"],
                        currency=website.currency_id,
                        quantity=1,
                        product=product_or_template.sudo(),
                        partner=partner,
                    )["total_excluded"]
                }
            )
        return combination_info
