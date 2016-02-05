# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp.addons.website_sale.controllers.main import website_sale
from openerp.http import request


class website_sale(website_sale):

    def _get_search_domain(self, search, category, attrib_values):
        cr, uid, context, pool = (
            request.cr, request.uid, request.context, request.registry)
        domain = super(website_sale, self)._get_search_domain(
            search, category, attrib_values)
        if search:
            for srch in search.split(" "):
                public_categ_ids = pool['product.public.category'].search(
                    cr, uid, [('name', 'ilike', srch)], context=context)
                domain = ['|'] + domain + [
                    '|', ('attribute_line_ids.value_ids.name', 'ilike', srch),
                    ('public_categ_ids', 'child_of', public_categ_ids)]
        return domain
# vim:expandtab:tabstop=4:softtabstop=4:shiftwidth=4:
