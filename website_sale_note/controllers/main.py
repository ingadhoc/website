# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import http
from openerp.http import request
from openerp.addons.website_sale.controllers.main import website_sale


class website_sale(website_sale):

    @http.route(
        ['/shop/payment/add_note'], type='json', auth="public", website=True)
    def add_note(self, internal_notes, **post):
        print 'aaaaaaaaa'
        print 'bbbbbbbbb'
        print 'aaaaaaaaa', internal_notes
        context = request.context
        order = request.website.sale_get_order(context=context)
        if order:
            order.write({'internal_notes': internal_notes})
