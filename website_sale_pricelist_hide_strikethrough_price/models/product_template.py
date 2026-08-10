from odoo import models
from odoo.http import request


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def _get_additionnal_combination_info(self, product_or_template, quantity, uom, date, website):
        # Used on the product page and by the variant-change RPC. If the active
        # pricelist hides strikethrough prices, neutralize the flags that drive
        # both the discount strikethrough (.oe_default_price) and the compare
        # price (.oe_compare_list_price). The frontend JS re-reads these values,
        # so no template/JS override is needed.
        res = super()._get_additionnal_combination_info(product_or_template, quantity, uom, date, website)
        # `super()` already dereferences `request.pricelist` (eCommerce/feed flows
        # are the only callers), so the request is guaranteed bound and set here.
        pricelist = request.pricelist
        if pricelist and pricelist.website_hide_strikethrough_price:
            res["has_discounted_price"] = False
            res["list_price"] = res.get("price")
            res.pop("compare_list_price", None)
        return res

    def _get_sales_prices(self, website):
        # Used on the /shop grid tiles. Dropping `base_price` hides the grid
        # strikethrough (<del>) and, since the automatic ribbon relies on the
        # same value, its "Sale" ribbon too.
        res = super()._get_sales_prices(website)
        pricelist = request.pricelist
        if pricelist and pricelist.website_hide_strikethrough_price:
            for vals in res.values():
                vals.pop("base_price", None)
        return res
