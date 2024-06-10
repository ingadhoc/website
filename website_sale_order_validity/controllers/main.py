from odoo import http, fields
from odoo.http import request
from werkzeug.utils import redirect
from odoo.addons.payment.controllers import portal as payment_portal


class WebsiteSaleController(http.Controller):
    @http.route('/update_date_prices_and_validity', type='http', auth='public', website=True)
    def update_validity_and_redirect(self):
        sale_order_id = request.session.get('sale_order_id')
        if sale_order_id:
            sale_order = request.env['sale.order'].sudo().browse(sale_order_id)
            if request.env['sale.order']._fields.get('validity_days'):
                sale_order.update_date_prices_and_validity()
            else:
                sale_order.action_update_prices()
                sale_order._compute_validity_date()
        return redirect('/shop/cart')


class WebsiteSale(payment_portal.PaymentPortal):
    @http.route()
    def shop_payment(self, **post):
        res = super().shop_payment(**post)
        order = request.website.sale_get_order()
        if order and order.validity_date and order.validity_date < fields.Date.today():
            res.qcontext.pop('payment_methods_sudo', '')
            res.qcontext.pop('tokens_sudo', '')
            res.qcontext.update({'show_update_cart': True})
        return res
