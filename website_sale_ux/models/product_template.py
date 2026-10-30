##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def _get_additional_combination_info(
        self, product_or_template, quantity, uom, website, pricelist, fiscal_position, **kwargs
    ):
        combination_info = super()._get_additional_combination_info(
            product_or_template, quantity, uom, website, pricelist, fiscal_position, **kwargs
        )
        # `/website_sale/get_combination_info` is public, so the reference only travels when the
        # shop is actually showing it. A template with several variants has none of its own, and a
        # dynamic combination may have no variant yet: both come back empty and the page hides it.
        if website.is_view_active("website_sale_ux.website_internal_ref_product"):
            combination_info["default_code"] = (
                product_or_template.default_code if product_or_template.is_product_variant else False
            )
        return combination_info
