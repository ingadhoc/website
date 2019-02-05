##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import api, models


class ProductPackLine(models.Model):

    _inherit = 'product.pack.line'

    @api.multi
    def get_sale_order_line_vals(self, line, order):
        """ Overwrite in order to proper show it in website cart. There we do
        not show the discount column so we wan to show the price_unit with the
        discount included.
        """
        self.ensure_one()
        vals = super(ProductPackLine, self).get_sale_order_line_vals(
            line, order)
        if self._context.get('website_id', False):
            vals.update({
                'price_unit': vals['price_unit'] * (
                    1.0 - vals['discount']/100),
                'discount': 0.0,
            })
        return vals
