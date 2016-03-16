# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp.http import request
from openerp import http, SUPERUSER_ID


class pos_website_sale(http.Controller):
    @http.route(
        ['/shop/clear_cart_line'], type='json', auth="public", website=True)
    def clear_cart_line(self, line_id, **kw):
        cr, context, pool = (
            request.cr, request.context, request.registry)
        pool['sale.order.line'].unlink(
            cr, SUPERUSER_ID, line_id, context=context)
