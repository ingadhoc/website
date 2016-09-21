# -*- coding: utf-8 -*-

import logging

from openerp.addons.web import http
from openerp.addons.web.http import request
from openerp.addons.website.controllers.main import Website as controllers
from openerp.addons.website.models.website import slugify
from openerp.tools.translate import _
from openerp.addons.website_search.controllers.html2text import html2text

logger = logging.getLogger(__name__)

controllers = controllers()


class WebsiteSearch(http.Controller):
    _results_per_page = 10
    _max_text_content_len=500
    _text_segment_back=100
    _text_segment_forward=300
    _min_search_len=3
    _search_on_pages=True
    _search_on_blogposts=True
    _search_on_comments=True
    _search_on_customers=True
    _search_on_jobs=True
    _search_on_products=True
    _case_sensitive=False
    _search_advanced=False



    def _removeSymbols(self, html_txt, symbol1, symbol2=False):

        if not symbol1 and not symbol2:
            return html_txt

        # Function to eliminate text between: symbol1 and symbol2
        index=html_txt.find(symbol1)
        start=0
        txt=''
        while index>0:
            if symbol2:
                index2=html_txt.find(symbol2, index)
                if index2<=0:
                    break
            else:
                index2=index+len(symbol1)-1
            txt+=html_txt[start:index]
            start=index2+1
            index=html_txt.find(symbol1, start)

        if len(txt)==0:
            return html_txt

        return txt

    def _module_installed(self, cr, module_name):

        if not module_name:
            return False

        cr.execute("SELECT count(*) FROM ir_module_module WHERE name='%s' AND state='installed'" % module_name)
        return (cr.fetchone()[0]==1)

    def _normalize_bool(self, param):

       res=False
       if param:
            try:
                param=int(param)
                res= not (param==0)
            except Exception:
                res=True

       return res

    def _normalize_int(self, param):

       res=0
       if param:
            try:
                res=int(param)
            except Exception:
                res=0

       return res

    @http.route(['/search'], type='http', auth="public", website=True)
    def search_page(self, search_advanced=False, search_on_pages=True, search_on_blogposts=True, search_on_comments=True, search_on_customers=True,
                       search_on_jobs=True, search_on_products=True, case_sensitive=False, search='', **post):

        # Process search parameters
        if isinstance(search_on_pages, unicode):
            self._search_on_pages=self._normalize_bool(search_on_pages)
        if isinstance(search_on_blogposts, unicode):
            self._search_on_blogposts=self._normalize_bool(search_on_blogposts)
        if isinstance(search_on_comments, unicode):
            self._search_on_comments=self._normalize_bool(search_on_comments)
        if isinstance(search_on_customers, unicode):
            self._search_on_customers=self._normalize_bool(search_on_customers)
        if isinstance(search_on_jobs, unicode):
            self._search_on_jobs=self._normalize_bool(search_on_jobs)
        if isinstance(search_on_products, unicode):
            self._search_on_products=self._normalize_bool(search_on_products)
        if isinstance(case_sensitive, unicode):
            self._case_sensitive=self._normalize_bool(case_sensitive)
        self._search_advanced=False

        user = request.registry['res.users'].browse(request.cr, request.uid, request.uid, context=request.context)
        values = {'user': user,
                  'is_public_user': user.id == request.website.user_id.id,
                  'header': post.get('header', dict()),
                  'searches': post.get('searches', dict()),
                  'results_count': 0,
                  'results': dict(),
                  'pager': None,
                  'search_on_pages': self._search_on_pages,
                  'search_on_blogposts': self._search_on_blogposts,
                  'search_on_comments': self._search_on_comments,
                  'search_on_customers': self._search_on_customers,
                  'search_on_jobs': self._search_on_jobs,
                  'search_on_products': self._search_on_products,
                  'case_sensitive': self._case_sensitive,
                  'search_advanced': False,
                  'sorting': False,
                  'search': search
                  }

        return request.website.render("website_search.search_page", values)



    @http.route(['/search_advanced'], type='http', auth="public", website=True)
    def search_page_advanced(self, search_advanced=True, search_on_pages=True, search_on_blogposts=True, search_on_comments=True, search_on_customers=True,
                       search_on_jobs=True, search_on_products=True, case_sensitive=False, search='', **post):

        # Process search parameters
        if isinstance(search_on_pages, unicode):
            self._search_on_pages=self._normalize_bool(search_on_pages)
        if isinstance(search_on_blogposts, unicode):
            self._search_on_blogposts=self._normalize_bool(search_on_blogposts)
        if isinstance(search_on_comments, unicode):
            self._search_on_comments=self._normalize_bool(search_on_comments)
        if isinstance(search_on_customers, unicode):
            self._search_on_customers=self._normalize_bool(search_on_customers)
        if isinstance(search_on_jobs, unicode):
            self._search_on_jobs=self._normalize_bool(search_on_jobs)
        if isinstance(search_on_products, unicode):
            self._search_on_products=self._normalize_bool(search_on_products)
        if isinstance(case_sensitive, unicode):
            self._case_sensitive=self._normalize_bool(case_sensitive)
        self._search_advanced=True

        user = request.registry['res.users'].browse(request.cr, request.uid, request.uid, context=request.context)
        values = {'user': user,
                  'is_public_user': user.id == request.website.user_id.id,
                  'header': post.get('header', dict()),
                  'searches': post.get('searches', dict()),
                  'results_count': 0,
                  'results': dict(),
                  'pager': None,
                  'search_on_pages': self._search_on_pages,
                  'search_on_blogposts': self._search_on_blogposts,
                  'search_on_comments': self._search_on_comments,
                  'search_on_customers': self._search_on_customers,
                  'search_on_jobs': self._search_on_jobs,
                  'search_on_products': self._search_on_products,
                  'case_sensitive': self._case_sensitive,
                  'search_advanced': True,
                  'sorting': False,
                  'search': search
                  }


        return request.website.render("website_search.search_page_advanced", values)


    # Low priority
    #TODO: Include results per page option?
    #TODO: Include order criteria option?


    @http.route(['/search_results',
                 '/search_results/page/<int:page>'
                 ], type='http', auth="public", website=True)
    def search_results(self, page=1, sorting='date', search='', **post):
        cr, uid, context = request.cr, request.uid, request.context

        if len(search)<self._min_search_len:
            return request.website.render("website_search.error_search_len", None)

        lang = request.context.get('lang')
        default_website_lang=request.website.default_lang_code[0:2]
        pages_use_translations= (default_website_lang!=lang[0:2])
        db_use_translations=(lang[0:2]!='en')

        # Check which modules are installed
        website_blog_installed = self._module_installed(cr, 'website_blog')
        website_partner_installed = self._module_installed(cr, 'website_partner')
        website_hr_recruitment_installed = self._module_installed(cr, 'website_hr_recruitment')
        website_sale_installed = self._module_installed(cr, 'website_sale')

        # Define search scope
        search_on_pages=self._search_on_pages
        search_on_blogposts=self._search_on_blogposts and website_blog_installed
        search_on_comments=self._search_on_comments and website_blog_installed
        search_on_customers=self._search_on_customers and website_partner_installed
        search_on_jobs=self._search_on_jobs and website_hr_recruitment_installed
        search_on_products=self._search_on_products and website_sale_installed
        case_sensitive=self._case_sensitive

        if not case_sensitive:
            search_lower=search.lower()

        url = "/search_results"
        sql_query=""


        # Check for other order criteria, if new order criteria added, add here
        if sorting=='date':
            sql_order_by='result_date desc'


        # Prepare Query to get search results on website pages

        if search_on_pages:
            if sql_query:
                sql_query+=' UNION ALL '
            if not pages_use_translations:
                sql_query+="""
                  SELECT DISTINCT 'Page' as result_type, vw.id as result_id, dt.name as result_name,  'website' as template_module, vw.arch as template_source, vw.website_meta_description, vw.website_meta_title, vw.website_meta_keywords, '/page/' as result_path, '' as result_image, 'es' as result_lang, '' as result_lang_text, vw.write_date as result_date
                  FROM  ir_ui_view vw, ir_model_data dt
                  WHERE dt.module='website' and dt.model='ir.ui.view'
                  and dt.res_id=vw.id and vw.type='qweb' and vw.mode='primary' and vw.page=true """
                if case_sensitive:
                  sql_query+="""and ( vw.arch ilike '%%%s%%' or vw.website_meta_description ilike '%%%s%%' or vw.website_meta_title ilike '%%%s%%' or vw.website_meta_keywords ilike '%%%s%%')
                """ % (search, search, search, search)
                else:
                  sql_query+="""and ( lower(vw.arch) ilike '%%%s%%' or lower(vw.website_meta_description) ilike '%%%s%%' or lower(vw.website_meta_title) ilike '%%%s%%' or lower(vw.website_meta_keywords) ilike '%%%s%%')
                """ % (search_lower, search_lower, search_lower, search_lower)
            else:
                sql_query+="""
                  SELECT DISTINCT 'Page' as result_type, vw.id as result_id, dt.name as result_name,  'website' as template_module, vw.arch as template_source, vw.website_meta_description, vw.website_meta_title, vw.website_meta_keywords, '/page/' as result_path, '' as result_image, tr.lang as result_lang, '' as result_lang_text, vw.write_date as result_date --tr.value as result_lang_text generated more rows and not used afterwards
                  FROM    ir_ui_view vw, ir_model_data dt, ir_translation tr
                  WHERE   tr.type='view' and tr.lang='%s' and tr.res_id =vw.id
                  and     dt.module='website' and dt.model='ir.ui.view'
                  and     dt.res_id=vw.id and vw.type='qweb' and vw.mode='primary' and vw.page=true """ % (lang)
                if case_sensitive:
                    sql_query+="""and     tr.value ilike '%%%s%%'""" % (search)
                else:
                    sql_query+="""and     lower(tr.value) ilike '%%%s%%'""" % (search_lower)


        if search_on_blogposts:
            if sql_query:
                sql_query+=' UNION ALL '
            if db_use_translations:
                sql_query+="""
                  SELECT DISTINCT 'Blog post' as result_type, blp.id as result_id, blp.name as result_name,  'website_blog' as template_module, tr.value as template_source, blp.website_meta_description, blp.website_meta_title, blp.website_meta_keywords,  '/blog/'||bl.name||'-'||bl.id|| '/post/' as result_path, '' as result_image, tr.lang as result_lang, '' as result_lang_text, blp.write_date as result_date --tr.value as result_lang_text generated more rows and not used afterwards
                  FROM ir_translation tr, blog_blog bl, blog_post blp
                  LEFT OUTER JOIN blog_post_blog_tag_rel tg_rel ON (tg_rel.blog_post_id=blp.id)
                  LEFT OUTER JOIN blog_tag tg ON (tg_rel.blog_tag_id=tg.id)
                  LEFT OUTER JOIN ir_translation tr2 ON (tr2.res_id=tg.id)
                  WHERE blp.blog_id=bl.id and tr.type='model' and tr.name='blog.post,content' and tr2.name='blog.tag,name'
                  and blp.website_published=true
                  and tr.res_id=blp.id and tr.lang='%s' """ % (lang)
                if case_sensitive:
                    sql_query+="""and ( tr.value ilike '%%%s%%' or tr2.value ilike '%%%s%%')""" % ( search, search)
                else:
                    sql_query+="""and ( lower(tr.value) ilike '%%%s%%' or lower(tr2.value) ilike '%%%s%%')""" % (search_lower, search_lower)
            else:
                sql_query+="""
                  SELECT DISTINCT 'Blog post' as result_type, blp.id as result_id, blp.name as result_name,  'website_blog' as template_module, blp.content as template_source, blp.website_meta_description, blp.website_meta_title, blp.website_meta_keywords, '/blog/'||bl.name||'-'||bl.id|| '/post/' as result_path, '' as result_image, '%s' as result_lang, '' as result_lang_text, blp.write_date as result_date
                  FROM blog_blog bl, blog_post blp
                  LEFT OUTER JOIN blog_post_blog_tag_rel tg_rel ON (tg_rel.blog_post_id=blp.id)
                  LEFT OUTER JOIN blog_tag tg ON (tg_rel.blog_tag_id=tg.id)
                  WHERE blp.website_published=true and blp.blog_id=bl.id """ % (lang)
                if case_sensitive:
                    sql_query+="""and ( blp.content ilike '%%%s%%' or blp.website_meta_title ilike '%%%s%%' or blp.website_meta_keywords ilike '%%%s%%' or tg.name ilike '%%%s%%')""" % (search, search, search, search)
                else:
                    sql_query+="""and ( lower(blp.content) ilike '%%%s%%' or lower(blp.website_meta_title) ilike '%%%s%%' or lower(blp.website_meta_keywords) ilike '%%%s%%' or lower(tg.name) ilike '%%%s%%')""" % (search_lower, search_lower, search_lower, search_lower)


        if search_on_comments:
            if sql_query:
                sql_query+=' UNION ALL '

            sql_query+="""
                  SELECT DISTINCT 'Blog post comment' as result_type, blp.id as result_id, blp.name as result_name,  'website_blog' as template_module, ml.body as template_source, '' as website_meta_description, '' as website_meta_title, '' as website_meta_keywords, '/blog/'||bl.name||'-'||bl.id|| '/post/' as result_path, '' as result_image, '' as result_lang, '' as result_lang_text, ml.write_date as result_date
                  FROM blog_blog bl, blog_post blp, mail_message ml
                  WHERE blp.website_published=true and ml.website_published=true and blp.blog_id=bl.id
                  and ml.res_id=blp.id and ml.model='blog.post' """
            if case_sensitive:
                sql_query+="""and ml.body ilike '%%%s%%'""" % (search)
            else:
                sql_query+="""and lower(ml.body) ilike '%%%s%%'""" % (search_lower)



        if search_on_customers:
            if sql_query:
                sql_query+=' UNION ALL '
            if db_use_translations:
                sql_query+="""
                  SELECT DISTINCT 'Customer' as result_type, rf.id as result_id, rf.name as result_name,  'website_customer' as template_module, tr.value as template_source, rf.website_meta_description, rf.website_meta_title, rf.website_meta_keywords, '/customers/' as result_path, '' as result_image, '%s' as result_lang, '' as result_lang_text, rf.write_date as result_date
                  FROM ir_translation tr, ir_translation tr2, res_partner rf
                  LEFT OUTER JOIN res_partner_res_partner_category_rel tg_rel ON (tg_rel.partner_id=rf.id)
                  LEFT OUTER JOIN res_partner_category tg ON (tg_rel.category_id=tg.id)
                  WHERE rf.website_published=true
                  and tr.type='model' and (tr.name='res.partner,website_description') --or tr.name='res.partner,website_short_description' )
                  and tr2.name='res.partner.category,name' and tr.res_id=rf.id and tr.lang='%s' """ %(lang, lang)
                if case_sensitive:
                    sql_query+="""and ( tr.value ilike '%%%s%%' or tr2.value ilike '%%%s%%')""" % (search, search)
                else:
                    sql_query+="""and ( lower(tr.value) ilike '%%%s%%' or lower(tr2.value) ilike '%%%s%%')""" % (search_lower, search_lower)
            else:
                sql_query+="""
                  SELECT DISTINCT 'Customer' as result_type, rf.id as result_id, rf.name as result_name,  'website_customer' as template_module, rf.website_description as template_source, rf.website_meta_description, rf.website_meta_title, rf.website_meta_keywords, '/customers/' as result_path, '' as result_image, '%s' as result_lang, '' as result_lang_text, rf.write_date as result_date
                  FROM res_partner rf
                  LEFT OUTER JOIN res_partner_res_partner_category_rel tg_rel ON (tg_rel.partner_id=rf.id)
                  LEFT OUTER JOIN res_partner_category tg ON (tg_rel.category_id=tg.id)
                  WHERE rf.website_published=true """ % (lang)
                if case_sensitive:
                    sql_query+="""and ( rf.website_short_description ilike '%%%s%%' or rf.website_description ilike '%%%s%%' or rf.website_meta_keywords ilike '%%%s%%' or
                        rf.website_meta_title ilike '%%%s%%' or rf.website_meta_description  ilike '%%%s%%'  or tg.name ilike '%%%s%%')""" % (search, search, search, search, search, search, )
                else:
                    sql_query+="""and ( lower(rf.website_short_description) ilike '%%%s%%' or lower(rf.website_description) ilike '%%%s%%' or lower(rf.website_meta_keywords) ilike '%%%s%%' or
                        lower(rf.website_meta_title) ilike '%%%s%%' or lower(rf.website_meta_description)  ilike '%%%s%%'  or lower(tg.name) ilike '%%%s%%')""" % (search_lower, search_lower, search_lower, search_lower, search_lower, search_lower, )



        if search_on_jobs:
            #Query for job opportunities
            if sql_query:
                sql_query+=' UNION ALL '
            sql_query+="""
                  SELECT DISTINCT 'Job' as result_type, jb.id as result_id, jb.name as result_name,  'website_hr_recruitment' as template_module, jb.website_description as template_source, jb.website_meta_description, jb.website_meta_title, jb.website_meta_keywords, '/jobs/detail/' as result_path, '' as result_image, '' as result_lang, '' as result_lang_text, jb.write_date as result_date
                  FROM hr_job jb
                  WHERE jb.website_published=true """
            if case_sensitive:
                    sql_query+="""and ( jb.website_description ilike '%%%s%%' or jb.website_meta_keywords ilike '%%%s%%' or
                        jb.website_meta_title ilike '%%%s%%' or jb.website_meta_description  ilike '%%%s%%'  or jb.name ilike '%%%s%%')""" % (search, search, search, search, search, )
            else:
                    sql_query+="""and ( lower(jb.website_description) ilike '%%%s%%' or lower(jb.website_meta_keywords) ilike '%%%s%%' or
                        lower(jb.website_meta_title) ilike '%%%s%%' or lower(jb.website_meta_description)  ilike '%%%s%%'  or lower(jb.name) ilike '%%%s%%')""" % (search_lower, search_lower, search_lower, search_lower, search_lower, )

        if search_on_products:
            # Query for product info (shop)
            if sql_query:
                sql_query+=' UNION ALL '
            sql_query+="""
                  SELECT DISTINCT 'Product' as result_type, pd.id as result_id, pd.name as result_name,  'website_sale' as template_module, pd.website_description as template_source, pd.website_meta_description, pd.website_meta_title, pd.website_meta_keywords, '/shop/product/' as result_path, '' as result_image, '' as result_lang, '' as result_lang_text, pd.write_date as result_date
                  FROM product_template pd
                  WHERE pd.website_published=true """
            if case_sensitive:
                    sql_query+="""and ( pd.website_description ilike '%%%s%%' or pd.website_meta_keywords ilike '%%%s%%' or
                        pd.website_meta_title ilike '%%%s%%' or pd.website_meta_description  ilike '%%%s%%'  or pd.name ilike '%%%s%%')""" % (search, search, search, search, search, )
            else:
                    sql_query+="""and ( lower(pd.website_description) ilike '%%%s%%' or lower(pd.website_meta_keywords) ilike '%%%s%%' or
                        lower(pd.website_meta_title) ilike '%%%s%%' or lower(pd.website_meta_description)  ilike '%%%s%%'  or lower(pd.name) ilike '%%%s%%')""" % (search_lower, search_lower, search_lower, search_lower, search_lower, )



        # Build query count
        if sql_query:
            sql_query_count="""SELECT count(distinct result_type||'-'||result_id  ) FROM ( %s ) as subquery""" % (sql_query)

        # Build query for results ordered
        if sql_query:
            limit=self._results_per_page
            offset=(page-1)*self._results_per_page
            sql_query_ordered="""SELECT distinct result_type, result_id, result_name,  template_module, template_source, website_meta_description, website_meta_title, website_meta_keywords, result_path, result_image, result_lang, result_lang_text, result_date
                                 FROM ( %s ) as subquery
                                 ORDER BY %s
                                 LIMIT %s
                                 OFFSET %s

                                 """ % (sql_query, sql_order_by, limit, offset)



        # Get results count for pager
        if sql_query_count:
            cr.execute(sql_query_count)
            results_count=cr.fetchone()[0] or 0

        url_args = {}
        if search:
            url_args['search'] = search
#        if search_on:
#            url_args['search_on'] = search_on
        if sorting:
            url_args['sorting'] = sorting
        pager = request.website.pager(url=url, total=results_count, page=page,
                                      step=self._results_per_page, scope=self._results_per_page,
                                      url_args=url_args)


        # Get results and prepare info to render results page
        user = request.registry['res.users'].browse(request.cr, request.uid, request.uid, context=request.context)
        values = {'user': user,
                  'is_public_user': user.id == request.website.user_id.id,
                  'header': post.get('header', dict()),
                  'searches': post.get('searches', dict()),
                  'results_per_page': self._results_per_page,
                  'last_result_showing': min(results_count, page*self._results_per_page),
                  'results_count': results_count,
                  'results': [],
                  'pager': pager,
                  'search_on_pages': search_on_pages,
                  'search_on_blogposts': self._search_on_blogposts,
                  'search_on_comments': self._search_on_comments,
                  'search_on_customers': self._search_on_customers,
                  'search_on_jobs': self._search_on_jobs,
                  'search_on_products': self._search_on_products,
                  'case_sensitive': self._case_sensitive,
                  'sorting': sorting,
                  'search': search,
                  }

        if sql_query_ordered:
            cr.execute(sql_query_ordered)
            for result in cr.fetchall():
                result_id= result[0] + '-' + str(result[1])
                result_data={
                        'type': result[0],
                        'type_txt': _(result[0]),
                        'id': result[1],
                        'name': result[2],
                        'template_name':result[3] + '.' + result[2],
                        'template_source':result[4],
                        'website_meta_description':result[5],
                        'website_meta_title': result[6],
                        'website_meta_keywords':result[7],
                        'url': result[8] + result[2],
                        'image': result[9],     # seleccionar una imagen por tipo
                        'lang': result[10],
                        'lang_text': result[11],
                        'date': result[12][8:10]+"/"+result[12][5:7]+"/"+result[12][0:4],
                        'ocurrences': 0,
                        'object': None
                    }
                # Prepare result content near searched keyword
                if result_data['type']=='Page':
                    # Render page html
                    try:
                        html=request.registry['ir.ui.view'].render(cr, uid, result_data['template_name'], context=context, **post)
                    except Exception:
                        html='<main>'+_('Unable to get text page')+'</main>'
                    start=html.find("<main>")
                    end=html.find("</main>")+7

                elif result_data['type']=='Blog post':
                    # Render blog post html
                    try:
                        url_array=result_data['url'].split('/')
                        url_array[2]=slugify(url_array[2])
                        url_array[4]=slugify(url_array[4])
                        result_data['url']='/'.join(url_array)
                        result_data['url']=result_data['url']+"-"+str(result_data["id"])
                        blog_post=request.registry['blog.post'].browse(cr, uid, int(result_data['id']), context=context)
                        result_data['object']=blog_post
                        html=request.registry['ir.ui.view'].render(cr, uid, "website_search.blog_post_content", {'blog_post': blog_post}, context=context)
                    except Exception:
                        html='<main>'+_('Unable to get blog post text')+'</main>'

                    start=0
                    end=len(html)

                elif result_data['type']=='Blog post comment':
                    # Render blog post html
                    try:
                        url_array=result_data['url'].split('/')
                        url_array[2]=slugify(url_array[2])
                        url_array[4]=slugify(url_array[4])
                        result_data['url']='/'.join(url_array)
                        result_data['url']=result_data['url']+"-"+str(result_data["id"])
                        html=result_data['template_source']
                    except Exception:
                        html='<main>'+_('Unable to get blog post comment text')+'</main>'

                    start=0
                    end=len(html)

                elif result_data['type']=='Customer':
                    # Render customer info html
                    try:
                        url_array=result_data['url'].split('/')
                        url_array[2]=slugify(url_array[2])
                        result_data['url']='/'.join(url_array)
                        result_data['url']=result_data['url']+"-"+str(result_data["id"])
                        customer=request.registry['res.partner'].browse(cr, uid, int(result_data['id']), context=context)
                        result_data['object']=customer
                        html=request.registry['ir.ui.view'].render(cr, uid, "website_search.customer_detail", {'partner': customer}, context=context)
                    except Exception:
                        html='<main>'+_('Unable to get customer text')+'</main>'

                    start=0
                    end=len(html)

                elif result_data['type']=='Job':
                    # Render job info html
                    try:
                        url_array=result_data['url'].split('/')
                        url_array[3]=slugify(url_array[3])
                        result_data['url']='/'.join(url_array)
                        result_data['url']=result_data['url']+"-"+str(result_data["id"])
                        job=request.registry['hr.job'].browse(cr, uid, int(result_data['id']), context=context)
                        result_data['object']=job
                        html=request.registry['ir.ui.view'].render(cr, uid, "website_search.job_detail", {'job': job}, context=context)
                    except Exception:
                        html='<main>'+_('Unable to get job text')+'</main>'

                    start=0
                    end=len(html)


                elif result_data['type']=='Product':
                    # Render product info html
                    try:
                        url_array=result_data['url'].split('/')
                        url_array[3]=slugify(url_array[3])
                        result_data['url']='/'.join(url_array)
                        result_data['url']=result_data['url']+"-"+str(result_data["id"])
                        product=request.registry['product.template'].browse(cr, uid, int(result_data['id']), context=context)
                        result_data['object']=product
                        html=request.registry['ir.ui.view'].render(cr, uid, "website_search.product_detail", {'product': product}, context=context)
                    except Exception:
                        html='<main>'+_('Unable to get product text')+'</main>'

                    start=0
                    end=len(html)




                # Keep key part of html page
                html=html[start:end]

                # Convert to text, eliminate all tags and #, \n, [, ] symbols, and text between []
                if html2text:
                    html = html2text(html.decode('utf-8')).encode('utf-8')
                    html = self._removeSymbols(html.decode('utf-8'), '[', ']').encode('utf-8')
                    html = self._removeSymbols(html.decode('utf-8'), '\n').encode('utf-8')
                    html = self._removeSymbols(html.decode('utf-8'), '#').encode('utf-8')



                # If not case sensitive search, apply lower function to search term and html
                if case_sensitive:
                    search_term=search
                    search_html=html
                else:
                    search_term=search_lower
                    search_html=html.lower()

                # Trim content to a maximum total characters to show in description with nearest text
                if len(search_html)>self._max_text_content_len:
                    index=search_html.find(str(search_term), 0)
                    start=max(0, index-self._text_segment_back)
                    end=min(len(search_html), index+self._text_segment_forward)
                    html_trim=html[start:end]
                    search_html_trim=search_html[start:end]
                    if start>0:
                        html_trim="..."+html_trim
                        search_html_trim="..."+search_html_trim
                    if end<len(search_html):
                        html_trim=html_trim+"..."
                        search_html_trim=search_html_trim+"..."
                    search_html=search_html_trim
                    html=html_trim

                # Find keyword in description text to force style to background yellow and bold text
                index=search_html.find(str(search_term), 0)
                index_start=0
                str_styled_search="<span style='font-weight: bold; font-size: 100%%; background-color: yellow;'>%s</span>" % str(search)
                html_styled=''
                ocurrences=0
                while index>=0:
                    ocurrences+=1
                    html_styled+=html[index_start:index]
                    html_styled+=str_styled_search
                    index_start=index+len(str(search_term))
                    index=search_html.find(str(search_term), index_start)
                html_styled+=html[index_start:]


                result_data['content']="<p>"+html_styled+"</p>"
                result_data['ocurrences']=ocurrences
                values['results'].append(result_data)

        # Render results
        return request.website.render("website_search.search_results", values)

