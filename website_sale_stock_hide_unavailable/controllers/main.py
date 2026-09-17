from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteSale(WebsiteSale):
    def _shop_lookup_products(self, options, post, search, website):
        term, product_count, products = super()._shop_lookup_products(options, post, search, website)
        if website.out_of_stock_display == "last" and products:
            unavailable = website._get_unavailable_tmpl_ids(products)
            if unavailable:
                # sorted() is stable: within each group the user's order (price,
                # name, novelty...) is preserved. The controller already holds
                # the full recordset in memory, so this is a re-sort, not a query
                # on the whole catalogue. Does not change product_count or paging.
                products = products.sorted(key=lambda p: p.id in unavailable)
        return term, product_count, products
