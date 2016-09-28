from openerp import api, models, fields,http
from openerp.http import request
from datetime import datetime
from openerp.addons.website_sale.controllers.main import website_sale as controller

class website_sale(controller):

    @http.route(['/shop',
        '/shop/page/<int:page>',
        '/shop/category/<model("product.public.category"):category>',
        '/shop/category/<model("product.public.category"):category>/page/<int:page>'
    ], type='http', auth="public", website=True)

    def shop(self, page=0, category=None, search='', **post):
        uid,context=request.uid,request.context

        categ_id=""

        if category!=None:
            categ_id=category.id

        data={
              "date":datetime.today(),
              "user_id":uid,
              "category_id":categ_id,
              "lang_id":request.env["res.lang"].search([('code','=',context["lang"])])[0].id,
              "search_user":search,
        }

        if category!=None or search!='':
            request.env["website.sale.tracker"].sudo().create(data)
        return super(website_sale, self).shop(page=page, category=category, search=search, **post)


    @http.route(['/shop/product/<model("product.template"):product>'], type='http', auth="public", website=True)
    def product(self, product, category='', search='', **kwargs):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        categ_id=""
        prod_id=""



        if product!=None:
            prod_id=product.id

        data={
              "date":datetime.today(),
              "user_id":uid,
              "category_id":category,
              "lang_id":request.env["res.lang"].search([('code','=',context["lang"])])[0].id,
              "search_user":search,
              "product_id":prod_id,
        }

        if  product!=None:
            request.env["website.sale.tracker"].sudo().create(data)
        return super(website_sale, self).product(product=product,category=category, search=search, **kwargs)

