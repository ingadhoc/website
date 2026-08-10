from odoo.addons.website_sale.controllers.product_configurator import (
    WebsiteSaleProductConfiguratorController,
)
from odoo.http import request


class WebsiteSaleProductConfigurator(WebsiteSaleProductConfiguratorController):
    def _get_strikethrough_price(self, product_or_template, currency, date, price, pricelist_rule_id=None):
        # The product/combo configurator dialog renders its own strikethrough from
        # this hook. Hide it when the active pricelist requests it.
        pricelist = request.pricelist
        if pricelist and pricelist.website_hide_strikethrough_price:
            return None
        return super()._get_strikethrough_price(
            product_or_template, currency, date, price, pricelist_rule_id=pricelist_rule_id
        )
