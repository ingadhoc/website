from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale

class WebsiteSale(WebsiteSale):

    @http.route(['/shop/confirmation'], type='http', auth="public", website=True, sitemap=False)
    def shop_payment_confirmation(self, **post):

        sale_order_id = request.session.get('sale_last_order_id')

        if sale_order_id:
            order = request.env['sale.order'].sudo().browse(sale_order_id)
            if order and order.website_id.website_hide_all_prices:
                return request.redirect('/request-quotation')

        return super().shop_payment_confirmation(**post)
