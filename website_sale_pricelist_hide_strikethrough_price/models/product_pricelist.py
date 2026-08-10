from odoo import fields, models


class ProductPricelist(models.Model):
    _inherit = "product.pricelist"

    website_hide_strikethrough_price = fields.Boolean(
        string="Hide strikethrough prices",
        help="Hide the strikethrough/compare prices (and the automatic discount "
        "ribbon) in the eCommerce for customers using this pricelist.",
    )
