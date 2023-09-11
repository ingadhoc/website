# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request


class WebsiteSale(http.Controller):
    @http.route(['/installment_prices'], type='json', auth="public", methods=['POST'], website=True)
    def product_installment(self, product_tmpl, product, **post):
        product_tmpl_id = request.env['product.template'].browse(int(product_tmpl)).exists()
        return product_tmpl_id._website_installment_variant_tree(int(product))

    @http.route(['/installment_page/<model("product.template"):product>'], type='http', auth="public", methods=['GET'], website=True)
    def page_product_installment(self, product, **post):
        render_values = {
            'installment_tree': product._website_installment_tree(),
            'product_template': product,
        }
        return request.render("website_sale_installment.product_installment_page", render_values)
