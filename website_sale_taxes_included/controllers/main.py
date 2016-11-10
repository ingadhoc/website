# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
# from openerp import SUPERUSER_ID
from openerp import http
from openerp.http import request
# from openerp.tools.translate import _
# from openerp.addons.website.models.website import slug
from openerp.addons.website_sale.controllers.main import website_sale

# PPG = 20 # Products Per Page
# PPR = 4  # Products Per Row

# NOTA: no lo queremos poner en todos lados porque en realidad en algunos
# lugares el precio debe venir sin los impuestos desde la lista de precios
# por que los impuestos se agregan después


class website_sale(website_sale):

    @http.route([
        '/shop',
        '/shop/page/<int:page>',
        '/shop/category/<model("product.public.category"):category>',
        '/shop/category/<model("product.public.category"):category>/page/'
        '<int:page>'
    ], type='http', auth="public", website=True)
    def shop(self, page=0, category=None, search='', **post):
        context = request.context
        context['taxes_included'] = True
        return super(website_sale, self).shop(
            page=page, category=category, search=search, **post)

    @http.route(
        ['/shop/product/<model("product.template"):product>'], type='http',
        auth="public", website=True)
    def product(self, product, category='', search='', **kwargs):
        context = request.context
        context['taxes_included'] = True
        return super(website_sale, self).product(
            product, category=category, search=search, **kwargs)

    @http.route(
        ['/shop/get_unit_price'], type='json', auth="public", methods=['POST'],
        website=True)
    def get_unit_price(
            self, product_ids, add_qty, use_order_pricelist=False, **kw):
        context = request.context
        context['taxes_included'] = True
        return super(website_sale, self).get_unit_price(
            product_ids, add_qty,
            use_order_pricelist=use_order_pricelist, **kw)

    # for website_sale_options
    @http.route(
        ['/shop/modal'], type='json', auth="public", methods=['POST'],
        website=True)
    def modal(self, product_id, **kw):
        context = request.context
        context['taxes_included'] = True
        return super(website_sale, self).modal(product_id, **kw)
