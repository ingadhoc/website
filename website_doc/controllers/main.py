# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import http
from openerp.http import request
import logging

# from openerp.addons.web import http
# from openerp.addons.web.http import request
from openerp.addons.website.controllers.main import Website as controllers
# from openerp.addons.website.models.website import slugify
from openerp.tools.translate import _
from openerp.addons.website_doc.controllers.html2text import html2text

logger = logging.getLogger(__name__)

controllers = controllers()


class WebsiteDoc(http.Controller):

    @http.route([
        '/doc/how-to',
        '/doc/how-to/<model("website.doc.toc"):toc>',
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

    _results_per_page = 10
    _max_text_content_len = 500
    _text_segment_back = 100
    _text_segment_forward = 300
    _min_search_len = 3
    _search_on_pages = True
    _case_sensitive = False
    _search_advanced = False

    def _removeSymbols(self, html_txt, symbol1, symbol2=False):

        if not symbol1 and not symbol2:
            return html_txt

        # Function to eliminate text between: symbol1 and symbol2
        index = html_txt.find(symbol1)
        start = 0
        txt = ''
        while index > 0:
            if symbol2:
                index2 = html_txt.find(symbol2, index)
                if index2 <= 0:
                    break
            else:
                index2 = index + len(symbol1) - 1
            txt += html_txt[start:index]
            start = index2 + 1
            index = html_txt.find(symbol1, start)

        if len(txt) == 0:
            return html_txt

        return txt

    def _module_installed(self, cr, module_name):

        if not module_name:
            return False

        cr.execute(
            "SELECT count(*) FROM ir_module_module WHERE name='%s' AND state='installed'" % module_name)
        return (cr.fetchone()[0] == 1)

    def _normalize_bool(self, param):

        res = False
        if param:
            try:
                param = int(param)
                res = not (param == 0)
            except Exception:
                res = True

        return res

    def _normalize_int(self, param):

        res = 0
        if param:
            try:
                res = int(param)
            except Exception:
                res = 0

        return res

    @http.route(['/search'], type='http', auth="public", website=True)
    def search_page(self, search_on_pages=True, case_sensitive=False,
                    search='', **post):

        # Process search parameters
        if isinstance(search_on_pages, unicode):
            self._search_on_pages = self._normalize_bool(search_on_pages)
        if isinstance(case_sensitive, unicode):
            self._case_sensitive = self._normalize_bool(case_sensitive)
        self._search_advanced = False

        user = request.registry['res.users'].browse(
            request.cr, request.uid, request.uid, context=request.context)
        values = {'user': user,
                  'is_public_user': user.id == request.website.user_id.id,
                  'header': post.get('header', dict()),
                  'searches': post.get('searches', dict()),
                  'results_count': 0,
                  'results': dict(),
                  'pager': None,
                  'search_on_pages': self._search_on_pages,
                  'search_advanced': False,
                  'sorting': False,
                  'search': search
                  }

        return request.website.render("website_doc.search_page", values)

    # Low priority
    # TODO: Include results per page option?
    # TODO: Include order criteria option?

    @http.route(['/search_results',
                 '/search_results/page/<int:page>'
                 ], type='http', auth="public", website=True)
    def search_results(self, page=1, sorting='date', search='', **post):
        cr, uid, context = request.cr, request.uid, request.context

        if len(search) < self._min_search_len:
            return request.website.render("website_doc.error_search_len", None)

        lang = request.context.get('lang')
        default_website_lang = request.website.default_lang_code[0:2]
        pages_use_translations = (default_website_lang != lang[0:2])
        # db_use_translations = (lang[0:2] != 'en')

        # Define search scope
        search_on_pages = self._search_on_pages
        case_sensitive = self._case_sensitive

        if not case_sensitive:
            search_lower = search.lower()

        url = "/search_results"
        sql_query = ""

        # Check for other order criteria, if new order criteria added, add here
        if sorting == 'date':
            sql_order_by = 'result_date desc'

        # Prepare Query to get search results on website pages

        if search_on_pages:
            if sql_query:
                sql_query += ' UNION ALL '
            if not pages_use_translations:
                sql_query += """
                  SELECT DISTINCT 'Page' as result_type, vw.id as result_id, vw.name as result_name,  'website' as template_module, vw.content as template_source, 'doc/how-to' as result_path, '' as result_image, 'es' as result_lang, '' as result_lang_text, vw.write_date as result_date
                  FROM  website_doc_toc vw 
                  WHERE vw.is_article = True """
                if case_sensitive:
                    sql_query += """ and (vw.content ilike '%%%s%%' or vw.name ilike '%%%s%%')
                """ % (search, search)
                else:
                    sql_query += """and (lower(vw.content) ilike '%%%s%%' or lower(vw.name) ilike '%%%s%%')
                """ % (search_lower, search_lower)
            else:
                sql_query += """
                  SELECT DISTINCT 'Page' as result_type, vw.id as result_id, dt.name as result_name,  'website' as template_module, vw.arch_db as template_source, vw.website_meta_description, vw.website_meta_title, vw.website_meta_keywords, '/page/' as result_path, '' as result_image, tr.lang as result_lang, '' as result_lang_text, vw.write_date as result_date --tr.value as result_lang_text generated more rows and not used afterwards
                  FROM    website_doc_toc vw, ir_translation tr
                  WHERE   vw.is_article = True and tr.lang='%s' """ % (lang)
                if case_sensitive:
                    sql_query += """and     tr.value ilike '%%%s%%'""" % (
                        search)
                else:
                    sql_query += """and     lower(tr.value) ilike '%%%s%%'""" % (
                        search_lower)

        # Build query count

        if sql_query:
            sql_query_count = """SELECT count(distinct result_type||'-'||result_id  ) FROM ( %s ) as subquery""" % (
                sql_query)

        # Build query for results ordered
        if sql_query:
            limit = self._results_per_page
            offset = (page - 1) * self._results_per_page
            sql_query_ordered = """SELECT distinct result_type, result_id, result_name,  template_module, template_source, result_path, result_image, result_lang, result_lang_text, result_date
                                 FROM ( %s ) as subquery
                                 ORDER BY %s
                                 LIMIT %s
                                 OFFSET %s

                                 """ % (sql_query, sql_order_by, limit, offset)

        # Get results count for pager
        if sql_query_count:
            cr.execute(sql_query_count)
            results_count = cr.fetchone()[0] or 0

        url_args = {}
        if search:
            url_args['search'] = search
        if sorting:
            url_args['sorting'] = sorting
        pager = request.website.pager(url=url, total=results_count, page=page,
                                      step=self._results_per_page, scope=self._results_per_page,
                                      url_args=url_args)

        # Get results and prepare info to render results page
        user = request.registry['res.users'].browse(
            request.cr, request.uid, request.uid, context=request.context)
        values = {'user': user,
                  'is_public_user': user.id == request.website.user_id.id,
                  'header': post.get('header', dict()),
                  'searches': post.get('searches', dict()),
                  'results_per_page': self._results_per_page,
                  'last_result_showing': min(results_count, page * self._results_per_page),
                  'results_count': results_count,
                  'results': [],
                  'pager': pager,
                  'search_on_pages': search_on_pages,
                  'case_sensitive': self._case_sensitive,
                  'sorting': sorting,
                  'search': search,
                  }

        if sql_query:
            cr.execute(sql_query_ordered)
            for result in cr.fetchall():
                # result_id= result[0] + '-' + str(result[1])
                result_data = {
                    'type': result[0],
                    'type_txt': _(result[0]),
                    'id': result[1],
                    'name': result[2],
                    'template_name': result[3] + '.' + result[2],
                    'website_meta_description': result[4],
                    'url': "/doc/how-to/%s" % (result[1]),
                    'date': result[9][8:10] + "/" + result[9][5:7] + "/" + result[9][0:4],
                }
                # Prepare result content near searched keyword
                if result_data['type'] == 'Page':
                    # Render page html
                    try:
                        html = '<main>' + \
                            result_data['website_meta_description'] + '</main>'
                    except Exception:
                        html = '<main>' + \
                            _('Unable to get text page') + '</main>'
                    start = html.find("<main>")
                    end = html.find("</main>") + 7

                # Keep key part of html page
                html = html[start:end]

                # Convert to text, eliminate all tags and #, \n, [, ] symbols, and text
                # between []
                if html2text:
                    html = html2text(html.decode('utf-8')).encode('utf-8')
                    html = self._removeSymbols(
                        html.decode('utf-8'), '[', ']').encode('utf-8')
                    html = self._removeSymbols(
                        html.decode('utf-8'), '\n').encode('utf-8')
                    html = self._removeSymbols(
                        html.decode('utf-8'), '#').encode('utf-8')

                # If not case sensitive search, apply lower function to search term and
                # html
                if case_sensitive:
                    search_term = search
                    search_html = html
                else:
                    search_term = search_lower
                    search_html = html.lower()

                # Trim content to a maximum total characters to show in description
                # with nearest text
                if len(search_html) > self._max_text_content_len:
                    index = search_html.find(str(search_term), 0)
                    start = max(0, index - self._text_segment_back)
                    end = min(len(search_html), index +
                              self._text_segment_forward)
                    html_trim = html[start:end]
                    search_html_trim = search_html[start:end]
                    if start > 0:
                        html_trim = "..." + html_trim
                        search_html_trim = "..." + search_html_trim
                    if end < len(search_html):
                        html_trim = html_trim + "..."
                        search_html_trim = search_html_trim + "..."
                    search_html = search_html_trim
                    html = html_trim

                # Find keyword in description text to force style to background yellow
                # and bold text
                index = search_html.find(str(search_term), 0)
                index_start = 0
                str_styled_search = "<span style='font-weight: bold; font-size: 100%%; background-color: yellow;'>%s</span>" % str(
                    search)
                html_styled = ''
                ocurrences = 0
                while index >= 0:
                    ocurrences += 1
                    html_styled += html[index_start:index]
                    html_styled += str_styled_search
                    index_start = index + len(str(search_term))
                    index = search_html.find(str(search_term), index_start)
                html_styled += html[index_start:]
                result_data['content'] = "<p>" + html_styled + "</p>"
                result_data['ocurrences'] = ocurrences
                values['results'].append(result_data)

        return request.website.render("website_doc.search_results", values)
