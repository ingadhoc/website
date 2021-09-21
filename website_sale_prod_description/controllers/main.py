from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteSale(WebsiteSale):
    def _get_search_domain(self, search, category, attrib_values, search_in_description=True):
        domain = super()._get_search_domain(search,
                                            category, attrib_values,
                                            search_in_description=search_in_description)
        if search:
            for n, element in enumerate(domain):
                if type(element) == tuple and element[0] == 'description_sale':
                    domain[n] = ('description_website', domain[n][1], domain[n][2])
        return domain
