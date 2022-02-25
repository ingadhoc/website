from odoo import models


class ProductProduct(models.Model):

    _inherit = 'product.product'

    def _get_domain_locations(self):
        """ If we are on website and there isn't a warehouse or location on
        the context, we get only published warehouses
        """
        if self._context.get('website_id') and self._context.get('warehouse'):
            # _get_domain_locations no admite por contexto ninguna clave para evaluar stock en varios almacenes /
            # ubicaciones, entonces hacemos la busqueda nosotros y luego llamamos directamente a _get_domain_locations_ne
            company_id = self.env.context.get('force_company', self.env.company.id)
            location_ids = self.env['stock.warehouse'].search(
                [('website_published', '=', True), ('company_id', '=', company_id)]).mapped('view_location_id').ids
            return self._get_domain_locations_new(
                location_ids,
                company_id=self.env.context.get('force_company', False),
                compute_child=self.env.context.get('compute_child', True))
        else:
            return super()._get_domain_locations()
