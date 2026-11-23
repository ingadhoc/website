from odoo.addons.website_sale.controllers import main
from odoo.fields import Domain
from odoo.http import request, route


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

    @route(
        "/website_sale_stock_variant_preselect/first_available_combination",
        type="jsonrpc",
        auth="public",
        website=True,
        readonly=True,
    )
    def first_available_combination(self, product_template_id):
        """Return the stock-aware default combination of a template, as ptav ids.

        Called by the product carousel card before opening the product configurator, which
        otherwise starts on core's first combination in sequence. Returns an empty list for
        a template the visitor cannot buy on this website.
        """
        # `search` applies the record rules, so an unpublished template comes back empty
        # instead of raising an AccessError for the public user.
        product_template = request.env["product.template"].search(
            Domain("id", "=", int(product_template_id)) & Domain(request.website.sale_product_domain()),
            limit=1,
        )
        if not product_template:
            return []
        return product_template._get_first_available_combination().ids
