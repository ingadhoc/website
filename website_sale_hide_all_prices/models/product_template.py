from odoo import models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def _get_additional_combination_info(
        self, product_or_template, quantity, uom, website, pricelist, fiscal_position, **kwargs
    ):
        combination_info = super()._get_additional_combination_info(
            product_or_template, quantity, uom, website, pricelist, fiscal_position, **kwargs
        )
        if website.website_hide_all_prices:
            combination_info.pop("packaging_prices", None)
        return combination_info

    def _search_render_results_prices(self, mapping, combination_info):
        if self.env.website.website_hide_all_prices:
            return None
        return super()._search_render_results_prices(mapping, combination_info)
