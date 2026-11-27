from odoo import models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def _l10n_ar_vat_tax_name(self, taxes):
        """Names of the VAT taxes only, for the tax indication of the shop."""
        return ", ".join(taxes.filtered(lambda tax: tax.tax_group_id.l10n_ar_vat_afip_code).mapped("name"))

    def _get_sales_prices(self, pricelist_sudo, fiscal_position_sudo, website):
        prices = super()._get_sales_prices(pricelist_sudo, fiscal_position_sudo, website)
        if website and website.company_id.country_code == "AR":
            for template in self:
                # Same condition as the "Taxes calculated at checkout." disclaimer of the product page
                if (
                    template.type == "combo"
                    and website.tax_display == "tax_included"
                    and not all(
                        tax.price_include for tax in template.sudo().combo_ids.combo_item_ids.product_id.taxes_id
                    )
                ):
                    prices[template.id]["l10n_ar_vat_tax_name"] = ""
                    continue
                taxes = fiscal_position_sudo.map_tax(template.sudo().taxes_id._filter_taxes_by_company())
                prices[template.id]["l10n_ar_vat_tax_name"] = self._l10n_ar_vat_tax_name(taxes)
        return prices

    def _get_additional_combination_info(
        self, product_or_template, quantity, uom, website, pricelist, fiscal_position, **kwargs
    ):
        combination_info = super()._get_additional_combination_info(
            product_or_template, quantity, uom, website, pricelist, fiscal_position, **kwargs
        )
        if website and website.company_id.country_code == "AR":
            combination_info["l10n_ar_vat_tax_name"] = self._l10n_ar_vat_tax_name(combination_info["taxes"])
        return combination_info
