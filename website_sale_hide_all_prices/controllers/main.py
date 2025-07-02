from odoo import http
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.http import request
from odoo.tools.translate import _


class WebsiteSale(WebsiteSale):
    @http.route(["/shop/confirmation"], type="http", auth="public", website=True, sitemap=False)
    def shop_payment_confirmation(self, **post):
        sale_order_id = request.session.get("sale_last_order_id")

        if sale_order_id:
            order = request.env["sale.order"].sudo().browse(sale_order_id)
            if order and order.website_id.website_hide_all_prices:
                return request.redirect("/request-quotation")

        return super().shop_payment_confirmation(**post)

    def _get_shop_payment_values(self, order, **kwargs):
        payment_values = super()._get_shop_payment_values(order=order, **kwargs)
        if order and order.website_id.website_hide_all_prices:
            payment_values["submit_button_label"] = _("Request Quotation")
        return payment_values
