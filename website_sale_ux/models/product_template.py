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
        # A template with several variants has no internal reference of its own, and a dynamic
        # combination may have no variant created yet: both come back empty and the page hides it.
        combination_info["default_code"] = (
            product_or_template.default_code if product_or_template.is_product_variant else False
        )
        return combination_info
