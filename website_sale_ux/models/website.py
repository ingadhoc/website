##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, tools, fields


class Website(models.Model):

    _inherit = "website"

    disable_categories_search = fields.Boolean()

    def _search_get_details(self, search_type, order, options):
        res = super(Website, self)._search_get_details(search_type, order, options)
        if search_type == 'products' and self.sudo()._get_disable_categories_search():
            # borrar el elemento no es lo más elegante pero no vi otra forma facil
            # de heredar. no es caro en temas de performance ya que el metodo super
            # es super liviano (no hace busquedas ni nada)
            for idx, item in enumerate(res):
                if item.get('model') == 'product.public.category':
                    res.pop(idx)
        return res

    @tools.ormcache('self.id')
    def _get_disable_categories_search(self):
        self.ensure_one()
        return self.disable_categories_search
