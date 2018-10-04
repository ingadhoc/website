##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, api, fields
import odoo.addons.decimal_precision as dp


class DeliveryCarrier(models.Model):

    _inherit = 'delivery.carrier'

    taxed_price = fields.Float(
        compute='compute_taxed_price',
        string='Taxed Price',
        digits=dp.get_precision('Account'),
    )

    @api.depends
    def compute_taxed_price(self):
        company_id = self._context.get(
            'company_id', self.env.user.company_id.id)
        for carrier in self:
            taxed_price = \
                carrier.product_id.taxes_id.filtered(
                    lambda x: x.company_id.id == company_id).compute_all(
                    carrier.price, product=carrier.product_id)['total_included']
            carrier.taxed_price = taxed_price
