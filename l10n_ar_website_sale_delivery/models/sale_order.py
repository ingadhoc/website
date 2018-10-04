##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, api, fields
import odoo.addons.decimal_precision as dp


class SaleOrder(models.Model):

    _inherit = 'sale.order'

    amount_delivery_taxed = fields.Float(
        compute='compute_amount_delivery_taxed',
        string='Delivery Amount With Tax',
        digits=dp.get_precision('Account'),
    )

    @api.depends()
    def compute_amount_delivery_taxed(self):
        for rec in self:
            amount_delivery_taxed = 0.0
            for line in rec.order_line.filtered('is_delivery'):
                amount_delivery_taxed += line.tax_id.compute_all(
                    line.price_subtotal, product=line.product_id,
                    partner=self.partner_id)['total_included']
            rec.amount_delivery_taxed = amount_delivery_taxed
