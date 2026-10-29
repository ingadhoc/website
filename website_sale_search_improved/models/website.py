from odoo import models


class Website(models.Model):
    _inherit = "website"

    def _search_find_fuzzy_term(self, search_details, search, limit=1000, word_list=None):
        """Odoo performs a fuzzy search on the PostgreSQL server we need to remove non stored field from the search fields."""
        for search_detail in search_details:
            if search_detail["model"] == "product.template":
                search_detail["search_fields"] = [
                    f for f in search_detail["search_fields"] if self.check_stored_field(f.split("."))
                ]
        # Trigram search only joins one2many and many2many paths. Drop many2one paths on a copy,
        # because the exact search that runs afterwards reuses search_details.
        fuzzy_search_details = [
            dict(
                search_detail,
                search_fields=[f for f in search_detail["search_fields"] if not self.check_many2one_path(f.split("."))],
            )
            if search_detail["model"] == "product.template"
            else search_detail
            for search_detail in search_details
        ]
        return super()._search_find_fuzzy_term(fuzzy_search_details, search, limit=limit, word_list=word_list)

    def check_stored_field(self, fields_list, model="product.template"):
        """recursive method to check if a field path ends in a stored field"""
        field = self.env[model]._fields.get(fields_list[0])
        return self.check_stored_field(fields_list[1:], field.comodel_name) if field.relational else field.store

    def check_many2one_path(self, fields_list, model="product.template"):
        """recursive method to check if a field path goes through a many2one field"""
        field = self.env[model]._fields.get(fields_list[0])
        if field.type == "many2one":
            return True
        return self.check_many2one_path(fields_list[1:], field.comodel_name) if field.relational else False
