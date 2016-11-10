# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp.addons.website_sale.controllers.main import website_sale
from openerp.http import request
from openerp import http
from openerp.addons.website_sale.controllers import main as main_file
import werkzeug


class website_sale(website_sale):

    # VERSION ANTERIOR
    # def _get_search_domain(self, search, category, attrib_values):
    #     cr, uid, context, pool = (
    #         request.cr, request.uid, request.context, request.registry)
    #     domain = super(website_sale, self)._get_search_domain(
    #         search, category, attrib_values)
    #     if search:
    #         for srch in search.split(" "):
    #             public_categ_ids = pool['product.public.category'].search(
    #                 cr, uid, [('name', 'ilike', srch)], context=context)
    #             domain = [
    #                 '|', ('sale_ok', '=', True), '|',
    #                 ('attribute_line_ids.value_ids.name', 'ilike', srch),
    #                 ('public_categ_ids', 'child_of', public_categ_ids)
    #                 ] + domain
    #     return domain

    # def _get_search_domain(self, search, category, attrib_values):
    #     cr, uid, context, pool = (
    #         request.cr, request.uid, request.context, request.registry)
    #     print 'aaaaaaaaaa'
    #     domain = super(website_sale, self)._get_search_domain(
    #         search, category, attrib_values)
    #     # print 'domain', domain
    #     print 'search', search
    #     if search:
    #         sub_domain = []
    #         connector = []
    #         # todo split search for public categories
    #         for srch in search.split(" "):
    #             public_categ_ids = pool['product.public.category'].search(
    #                 cr, uid, [('name', 'ilike', srch)], context=context)
    #             sub_domain = connector + sub_domain + [
    #                 '|',
    #                 ('attribute_line_ids.value_ids.name', 'ilike', srch),
    #                 ('public_categ_ids', 'child_of', public_categ_ids)
    #             ]
    #             connector = ['|', ]
    #             # '&', ('sale_ok', '=', True),
    #         # sub_domain = ['|'] + sub_domain
    #         # domain = ['|'] + domain + sub_domain
    #             # domain = [
    #             #     '&', ('sale_ok', '=', True), '|',
    #             #     ('attribute_line_ids.value_ids.name', 'ilike', srch),
    #             #     ('public_categ_ids', 'child_of', public_categ_ids)
    #             #     ] + domain
    #                 # ]
    #     print 'domain', domain
    #     return domain

    def _get_search_domain(self, search, category, attrib_values):
        # TODO ver si usamos modulo de la oca de buscar por atributos
        # tambien pdoemos ver si cambiamos logica de que filtre como hace
        # vauxoo cambiando la parte de attrib_values comparando con or
        # TODO 2 ver si heredamos funcion en vez de sobrereescribir
        domain = request.website.sale_product_domain()

        # inicio cambio
        cr, uid, context, pool = (
            request.cr, request.uid, request.context, request.registry)
        if search:
            for srch in search.split(" "):
                public_categ_ids = pool['product.public.category'].search(
                    cr, uid, [('name', 'ilike', srch)], context=context)
                domain += [
                    '|', '|', '|', '|', '|', '|', ('name', 'ilike', srch),
                    ('barcode', 'ilike', srch),
                    ('description', 'ilike', srch),
                    ('description_sale', 'ilike', srch),
                    ('public_categ_ids', 'child_of', public_categ_ids),
                    ('attribute_line_ids.value_ids.name', 'ilike', srch),
                    ('product_variant_ids.default_code', 'ilike', srch)]
        # fin cambio

        if category:
            domain += [('public_categ_ids', 'child_of', int(category))]

        if attrib_values:
            attrib = None
            ids = []
            for value in attrib_values:
                if not attrib:
                    attrib = value[0]
                    ids.append(value[1])
                elif value[0] == attrib:
                    ids.append(value[1])
                else:
                    domain += [('attribute_line_ids.value_ids', 'in', ids)]
                    attrib = value[0]
                    ids = [value[1]]
            if attrib:
                domain += [('attribute_line_ids.value_ids', 'in', ids)]

        return domain

    @http.route()
    def shop(self, page=0, category=None, search='', **post):
        """
        If we have a search and category, clean category
        """
        if category and search:
            category = None
        return super(website_sale, self).shop(page, category, search, **post)


class QueryURL(object):
    def __init__(self, path='', **args):
        self.path = path
        self.args = args

    def __call__(self, path=None, **kw):
        if not path:
            path = self.path
        is_category = path.startswith('/shop/category/')
        for k, v in self.args.items():
            if is_category and k == 'search':
                continue
            kw.setdefault(k, v)
        l = []
        for k, v in kw.items():
            if v:
                if isinstance(v, list) or isinstance(v, set):
                    l.append(werkzeug.url_encode([(k, i) for i in v]))
                else:
                    l.append(werkzeug.url_encode([(k, v)]))
        if l:
            path += '?' + '&'.join(l)
        return path


main_file.QueryURL = QueryURL
