from odoo import http
from odoo.http import request
from werkzeug.utils import redirect


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
