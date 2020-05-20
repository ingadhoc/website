##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo import http


class WebsiteSaleCustom(WebsiteSale):

    @http.route()
    # TODO make optional
    def shop(self, page=0, category=None, search='', ppg=False, **post):
        """
        If we have a search and category, clean category
        """
        if category and search:
            category = None
        return super().shop(page=page, category=category, search=search, ppg=ppg, **post)
