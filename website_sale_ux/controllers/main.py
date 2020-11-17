##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.sale_product_configurator.controllers.main import ProductConfiguratorController
from odoo import http
from odoo.http import request


class WebsiteSaleCustom(WebsiteSale):

    @http.route()
    # TODO make optional
    def shop(self, page=0, category=None, search='', ppg=False, **post):
        """
        If we have a search and category, clean category
        """
        if category and search:
            category = None
        return super().shop(page=page, category=category, search=search, ppg=ppg, **post)


class ProductConfiguratorControllerCustom(ProductConfiguratorController):

    def _show_optional_products(self, product_id, variant_values, pricelist, handle_stock, **kw):
        product = request.env['product.product'].browse(int(product_id))
        combination = request.env['product.template.attribute.value'].browse(variant_values)

        add_qty = int(kw.get('add_qty', 1))

        no_variant_attribute_values = combination.filtered(lambda x: x.attribute_id.create_variant == 'no_variant')
        if no_variant_attribute_values:
            product = product.with_context(no_variant_attribute_values=no_variant_attribute_values)

        return request.env['ir.ui.view'].render_template("sale_product_configurator.optional_products_modal", {
            'product': product,
            'combination': combination,
            'add_qty': add_qty,
            'parent_name': product.name,
            'variant_values': variant_values,
            'pricelist': pricelist,
            'handle_stock': handle_stock,
        })
