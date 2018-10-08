##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.http import request, route
# from odoo.tools import config
from odoo import http


class L10nArWebsiteSale(WebsiteSale):

    # por ahora no los hacemos obligatorios porque deberian ser solo para el
    # commercial partner id, TODO encontrarle la vuelta y mejroarlo
    # def _get_mandatory_billing_fields(self):
    #     # para no romper los test de odoo
    #     res = super(L10nArWebsiteSale, self)._get_mandatory_billing_fields()
    #     if not config['test_enable']:
    #         res += ["zip"]
    #     return res + ["main_id_category_id", "main_id_number"]

    @route()
    def address(self, **kw):
        response = super(L10nArWebsiteSale, self).address(**kw)
        document_categories = request.env[
            'res.partner.id_category'].sudo().search([])
        Partner = request.env['res.partner'].with_context(
            show_address=1).sudo()
        response.qcontext.update({
            'document_categories': document_categories,
            'invoices':
                Partner.commercial_partner_id.invoice_ids and True or False,
        })
        return response

    # TODO review all this
    # NOTA: no lo queremos poner en todos lados porque en realidad en algunos
    # lugares el precio debe venir sin los impuestos desde la lista de precios
    # por que los impuestos se agregan después

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
        return super(L10nArWebsiteSale, self).shop(
            page=page, category=category, search=search, **post)

    @http.route(
        ['/shop/product/<model("product.template"):product>'], type='http',
        auth="public", website=True)
    def product(self, product, category='', search='', **kwargs):
        context = request.context
        context['taxes_included'] = True
        return super(L10nArWebsiteSale, self).product(
            product, category=category, search=search, **kwargs)

    @http.route(
        ['/shop/get_unit_price'], type='json', auth="public", methods=['POST'],
        website=True)
    def get_unit_price(
            self, product_ids, add_qty, use_order_pricelist=False, **kw):
        context = request.context
        context['taxes_included'] = True
        return super(L10nArWebsiteSale, self).get_unit_price(
            product_ids, add_qty,
            use_order_pricelist=use_order_pricelist, **kw)

    # for website_sale_options
    @http.route(
        ['/shop/modal'], type='json', auth="public", methods=['POST'],
        website=True)
    def modal(self, product_id, **kw):
        context = request.context
        context['taxes_included'] = True
        return super(L10nArWebsiteSale, self).modal(product_id, **kw)
