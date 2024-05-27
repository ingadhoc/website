from odoo import api, models

class Website(models.Model):

    _inherit = "website"

    def _search_find_fuzzy_term(self, search_details, search, limit=1000, word_list=None):
        """ If the 'allowFuzzy' key is enabled (it is by default) Odoo will perform a fuzzy search.
            However, it is executed directly on the PostgreSQL server. Therefore, the fields must be stored and cannot
            be many2one or many2many fields.
        """
        for search_detail in search_details:
            if search_detail['model'] == 'product.template':
                search_fields = search_detail['search_fields']
                smart_search_fields = self.sudo().env.ref('product.model_product_template').name_search_ids
                non_store_or_m2x_fields = smart_search_fields.filtered(
                    lambda f: not f.store or f.ttype in ['many2one', 'many2many']
                ).mapped('name')
                search_detail['search_fields'] = [field for field in search_fields if field not in non_store_or_m2x_fields]
        return super()._search_find_fuzzy_term(search_details, search, limit=limit, word_list=word_list)
