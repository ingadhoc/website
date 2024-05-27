##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.http import request


class WebsiteSale(WebsiteSale):

    def _add_search_subdomains_hook(self, srch):
        """ This method allows to order and filter products in the e-commerce by 'Price Range'
        """
        res = super()._add_search_subdomains_hook(srch)
        smart_search_domain = request.env['product.template']._search_smart_search('ilike', srch)
        return res + smart_search_domain
