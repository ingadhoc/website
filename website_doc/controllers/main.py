# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import http
from openerp.http import request


class WebsiteDoc(http.Controller):

    @http.route([
        '/doc/how-to',
        '/doc/how-to/<model("website.doc.toc"):toc>',
        # '/doc/how-to/<model("website.doc.toc"):toc>',
    ],
        type='http', auth="public", website=True)
    def article_doc_render(self, toc=None, **kwargs):
        # si estamos buscando en root los articulos son todos los que no tengan
        # padre, si no, son los hijos del toc
        if toc:
            titles = toc.child_ids
        else:
            toc = request.env['website.doc.toc']
            titles = toc.search([
                ('parent_id', '=', False),
                ('is_article', '=', False)])
        value = {
            'toc': toc,
            'titles': titles,
        }
        return request.website.render(
            "website_doc.documentation_post", value)
