##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import http
from odoo.http import request
import werkzeug.utils
from odoo.addons.website.controllers.main import Website as controllers

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

        if toc and toc.is_article:
            if toc.article_type == 'google_doc' and toc.google_doc_code:
                google_doc_url_template = request.env['ir.config_parameter'].sudo().get_param(
                    'website_doc.google_doc_url_template', default='https://docs.google.com/document/d/%s/view')
                return werkzeug.utils.redirect(google_doc_url_template % toc.google_doc_code)
            elif toc.article_type == 'url' and toc.article_url:
                return werkzeug.utils.redirect(toc.article_url)

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

        if not titles:
            articles = toc.article_ids
            if len(articles) == 1:
                return werkzeug.utils.redirect(articles.url_suffix)

        value = {
            'toc': toc,
            'titles': titles,
        }
        return request.render(
            "website_doc.documentation_post", value)

    @http.route([
        '/doc/read',
    ], type='json', auth="public", website=True)
    def read_status(self, record_id, model_name, **kwargs):
        _id = int(record_id)
        rec = request.env[model_name].browse(_id)
        rec.inverse_read(not rec.read_status)
        return bool(rec.read_status)
