from odoo import api, models
from ast import literal_eval

class Website(models.Model):

    _inherit = "website"

    def _search_find_fuzzy_term(self, search_details, search, limit=1000, word_list=None):
        """ Odoo performs a fuzzy search on the PostgreSQL server we need to remove non stored field from the search fields.
        """
        for search_detail in search_details:
            if search_detail['model'] == 'product.template':
                search_detail['search_fields'] = [f for f in search_detail['search_fields'] if self.check_stored_field(f.split('.'))]
        return super()._search_find_fuzzy_term(search_details, search, limit=limit, word_list=word_list)

    def check_stored_field(self, fields_list, model='product.template'):
        """ recursive method to check if a field path ends in a stored field
        """
        field = self.env[model]._fields.get(fields_list[0])
        return self.check_stored_field(fields_list[1:], field.comodel_name) if field.relational else field.store
