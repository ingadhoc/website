from odoo import models


class ProductProduct(models.Model):

    _inherit = 'product.product'

    def _get_domain_locations(self):
        """ If we are on website and there isn't a warehouse or location on
        the context, we get only published warehouses
        """
        if not self._context.get('website_id') or \
           self._context.get('warehouse') or \
           self._context.get('location'):
            return super(ProductProduct, self)._get_domain_locations()
        location_ids = self.env['stock.warehouse'].search(
            [('website_published', '=', True)]).mapped('view_location_id').ids
        return self._get_domain_locations_new(
            location_ids,
            company_id=self.env.context.get('force_company', False),
            compute_child=self.env.context.get('compute_child', True))
