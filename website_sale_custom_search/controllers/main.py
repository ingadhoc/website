# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp.addons.website_sale.controllers.main import website_sale


class website_sale(website_sale):

    def _get_search_domain(self, search, category, attrib_values):
        domain = super(website_sale, self)._get_search_domain(
            search, category, attrib_values)
        if search:
            for srch in search.split(" "):
                domain = ['|'] + domain + [
                    '|', ('attribute_line_ids.value_ids.name', 'ilike', srch),
                    ('public_categ_ids.name', 'ilike', srch)]
        return domain
# vim:expandtab:tabstop=4:softtabstop=4:shiftwidth=4:
