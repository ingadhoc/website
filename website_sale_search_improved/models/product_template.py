from odoo import api, models
from ast import literal_eval


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.model
    def _search_get_detail(self, website, order, options):
        """ Enhance the search functionality in the e-commerce module by adding extra fields for the search.
            Odoo will attempt to match the search term exactly within these additional fields.
        """
        res = super()._search_get_detail(website, order, options)
        if self.env['ir.config_parameter'].sudo().get_param('website_sale_search_improved.extend_search_fields'):
            extra_search_fields = literal_eval(self.env['ir.config_parameter'].sudo().get_param('website_sale_search_improved.search_fields'))
            res['search_fields'] = res['search_fields'] + extra_search_fields
        return res
