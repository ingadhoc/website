##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import website_sale


class website_sale(website_sale):

    @http.route(
        ['/shop/payment/add_note'], type='json', auth="public", website=True)
    def add_note(self, internal_notes, **post):
        context = request.context
        order = request.website.sale_get_order(context=context)
        if order:
            order.write({'internal_notes': internal_notes})
