from odoo import models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def _get_additional_combination_info(
        self, product_or_template, quantity, uom, website, pricelist, fiscal_position, **_kwargs
    ):
        # Used on the product page and by the variant-change RPC. If the active
        # pricelist hides strikethrough prices, neutralize the flags that drive
        # both the discount strikethrough (.oe_default_price) and the compare
        # price (.oe_compare_list_price). The frontend JS re-reads these values,
        # so no template/JS override is needed.
        res = super()._get_additional_combination_info(
            product_or_template=product_or_template,
            quantity=quantity,
            uom=uom,
            website=website,
            pricelist=pricelist,
            fiscal_position=fiscal_position,
            **_kwargs,
        )
        if pricelist and pricelist.website_hide_strikethrough_price:
            res["has_discounted_price"] = False
            res["list_price"] = res.get("price")
            res.pop("compare_list_price", None)
        return res

    def _get_sales_prices(self, pricelist_sudo, fiscal_position_sudo, website):
        # Used on the /shop grid tiles. Dropping `base_price` hides the grid
        # strikethrough (<del>) and, since the automatic ribbon relies on the
        # same value, its "Sale" ribbon too.
        res = super()._get_sales_prices(pricelist_sudo, fiscal_position_sudo, website)
        if pricelist_sudo and pricelist_sudo.website_hide_strikethrough_price:
            for vals in res.values():
                vals.pop("base_price", None)
        return res
