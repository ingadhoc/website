# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
import openerp
from openerp import http
from openerp.http import request


class website_sale(openerp.addons.website_sale.controllers.main.website_sale):

    @http.route(
        ['/shop/payment/add_note'], type='json', auth="public", website=True)
    def add_note(self, internal_notes, **post):
        context = request.context
        order = request.website.sale_get_order(context=context)
        order.write({'internal_notes': internal_notes})
