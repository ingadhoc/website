from odoo.addons.website_sale.controllers import main


class WebsiteSale(main.WebsiteSale):
    def _prepare_product_values(self, product, category, **kwargs):
        """Ask for the stock-aware default combination on the product page.

        Core resolves the default combination with `_get_first_possible_combination`,
        which walks the configured attribute order and never looks at stock: when the
        first variant is sold out the page renders as unavailable and the visitor may
        believe the whole product is (task #72834).

        The flag travels on the product record, not on the request, so it reaches the
        `_get_combination_info()` call of this page only: the shop grid and the website
        product blocks keep core's behaviour. A visitor who picked attributes already
        goes through the `attribute_values` branch, which we leave untouched.
        """
        if not kwargs.get("attribute_values"):
            product = product.with_context(website_sale_preselect_available_variant=True)
        return super()._prepare_product_values(product, category, **kwargs)
