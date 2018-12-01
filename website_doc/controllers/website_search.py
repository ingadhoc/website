##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import http
from odoo.http import request
from odoo.tools.translate import _
import logging
_logger = logging.getLogger(__name__)
try:
    import html2text
except ImportError:
    _logger.debug('Cannot import external_dependency html2text')


class WebsiteDoc(http.Controller):

    _results_per_page = 20
    _max_text_content_len = 500
    _text_segment_back = 100
    _text_segment_forward = 300
    _min_search_len = 3

    # we make doc required and we only search inside one doc
    @http.route([
        '/doc/<model("website.doc.toc"):doc>/search_results',
        '/doc/<model("website.doc.toc"):doc>/search_results/page/<int:page>',
    ], type='http', auth="public", website=True)
    def search_results(
            self, doc, page=1, search='', **post):

        if len(search) < self._min_search_len:
            values = {
                'doc': doc,
                'search': search,
            }
            return request.render("website_doc.error_search_len", values)

        env = request.env
        doc_table = env['website.doc.toc']._table
        # primero buscamos con ilike para tener resultados mas exactos
        # y buscamos para campo name y luego para contenido
        # luego repetimos con operador %
        env.cr.execute("SELECT set_limit(0.3);")
        results = doc.browse()
        for operator in ['ilike', '%']:
            for field in ['name', 'content']:
                # como el fuzzy search no nos funciona para content, por ahora
                # usamos smart search
                if operator == '%' and field == 'content':
                    operator = 'ilike'
                    # buscamosc copn sudo porque ahora ir.model esta solo
                    # para empleados y entonces si no da error al buscar
                    # con usuarios portal
                    results += doc.sudo().search([
                        ('id', 'child_of', doc.id),
                        ('id', 'not in', results.ids),
                        ('smart_search', operator, search),
                    ],)
                    continue
                results += doc.search([
                    ('id', 'child_of', doc.id),
                    ('id', 'not in', results.ids),
                    (field, operator, search),
                ], order="similarity(%s.%s, '%s') DESC" % (
                    doc_table, field, search))

        # hacemos esto para filtar por los articulos que puede ver el usuario
        # el exists no funciona porque se ve que al usar doc.sudo() en el
        # recordset ya queda mal
        # results = results.exists()
        results = doc.search([('id', 'in', results.ids)])
        results_count = len(results)
        url = request.httprequest.url
        url = "/doc/%i/search_results" % (doc.id)
        # url = "/search_results"
        url_args = {}
        if search:
            url_args['search'] = search

        pager = request.website.pager(
            url=url, total=results_count, page=page,
            step=self._results_per_page, scope=self._results_per_page,
            url_args=url_args)

        values = {
            'header': post.get('header', dict()),
            'searches': post.get('searches', dict()),
            'results_per_page': self._results_per_page,
            'last_result_showing': min(
                results_count, page * self._results_per_page),
            'results_count': results_count,
            'results': [],
            'pager': pager,
            'doc': doc,
            'search': search,
        }

        # obtenemos valores solo para los que queremos postrar en la page
        offset = (page - 1) * self._results_per_page
        for result in results[offset:offset + self._results_per_page]:
            result_data = {
                'toc': result,
                'name': result.name,
                'url': result.url_suffix,
            }
            # Render page html
            try:
                html = '<main>%s%s</main>' % (
                    result.name, result.content or '')
            except Exception:
                html = '<main>' + \
                    _('Unable to get text page') + '</main>'
            start = html.find("<main>")
            end = html.find("</main>") + 7

            # Keep key part of html page
            html = html[start:end]

            # Convert to text, eliminate all tags and #, \n, [, ] symbols,
            # and text between []

            html = html2text.html2text(html)
            html = self._removeSymbols(
                html, '[', ']')
            html = self._removeSymbols(
                html, '\n')
            html = self._removeSymbols(
                html, '#')

            # If not case sensitive search, apply lower function to search
            # term and html
            search_term = search.lower()
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

            # Find keyword in description text to force style to background
            # yellow and bold text
            index = search_html.find(str(search_term), 0)
            index_start = 0
            str_styled_search = (
                "<span style='font-weight: bold; font-size: 100%%;"
                "background-color: yellow;'>%s</span>" % str(
                    search))
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

        return request.render("website_doc.search_results", values)

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
