##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo.http import request
from odoo import http, SUPERUSER_ID
from odoo.addons.website_sale.controllers.main import website_sale


class website_sale(website_sale):

    @http.route(
        ['/shop/clear_cart_line'], type='json', auth="public", website=True)
    def clear_cart_line(self, line_id, **post):
        cr, context, pool = (
            request.cr, request.context, request.registry)
        pool['sale.order.line'].unlink(
            cr, SUPERUSER_ID, line_id, context=context)
