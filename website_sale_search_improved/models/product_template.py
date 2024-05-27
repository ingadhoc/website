from odoo import api, models

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.model
    def _search_get_detail(self, website, order, options):
        """ Enhance the search functionality in the e-commerce module by adding extra fields for the search.
            Odoo will attempt to match the search term exactly within these additional fields.
        """

        res = super()._search_get_detail(website, order, options)
        smart_search_fields = self.sudo().env.ref('product.model_product_template').name_search_ids
        res['search_fields'] = res['search_fields'] + smart_search_fields.mapped('name')
        return res
