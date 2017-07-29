# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import http
from openerp.http import request
import logging
import werkzeug.utils
# from openerp.addons.web import http
# from openerp.addons.web.http import request
from openerp.addons.website.controllers.main import Website as controllers
# from openerp.addons.website.models.website import slugify

logger = logging.getLogger(__name__)

controllers = controllers()


class WebsiteDoc(http.Controller):

    @http.route([
        '/doc/how-to',
    ],
        type='http', auth="public", website=True)
    def old_how_to_redirect(self, **kwargs):
        # just in case some old link to how-to remains active
        return werkzeug.utils.redirect('/doc')

    @http.route([
        # we have add route doc on link but we add this for compatibility with
        # old links
        '/doc/<model("website.doc.toc"):toc>',
        # we have replace route url from /doc/how-to/ to /doc/ but we keep
        # this for old links
        '/doc/how-to/<model("website.doc.toc"):toc>',
    ],
        type='http', auth="public", website=True)
    def article_doc_redirect(self, toc, **kwargs):
        return werkzeug.utils.redirect(toc.url_suffix)

    @http.route([
        # '/doc/how-to',
        '/doc',
        '/doc/<model("website.doc.toc"):doc>/<model("website.doc.toc"):toc>',
        # '/doc/<model("website.doc.toc"):doc>/<model("website.doc.toc"):toc>/'
        # '<string:uuid>',
    ],
        type='http', auth="public", website=True)
    def article_doc_render(
            self, doc=None, toc=None, **kwargs):
        # TODO restringir acceso (lo ve juan)
        # account_res = request.env['sale.subscription']
        # if uuid:
        #     account = account_res.sudo().browse(account_id)
        #     if uuid != account.uuid or account.state == 'cancelled':
        #         raise NotFound()
        #     if request.uid == account.partner_id.user_id.id:
        #         account = account_res.browse(account_id)
        # else:
        #     account = account_res.browse(account_id)

        if not toc:
            toc = request.env['website.doc.toc']

        # si estamos buscando en root los articulos son todos los que no tengan
        # padre, si no, son los hijos del toc
        if toc:
            titles = toc.child_ids
        else:
            titles = toc.search([
                ('parent_id', '=', False),
                ('is_article', '=', False)])

        value = {
            'toc': toc,
            'titles': titles,
        }
        return request.website.render(
            "website_doc.documentation_post", value)

    @http.route([
        '/doc/read',
    ], type='json', auth="public", website=True)
    def read(self, id, object, **kwargs):
        _id = int(id)
        rec = request.env[object].browse(_id)
        # rec.read_status = not rec.read_status
        rec.inverse_read(not rec.read_status)
        return bool(rec.read_status)
