# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, api, fields
# from openerp.exceptions import Warning
import openerp.addons.decimal_precision as dp
import logging
_logger = logging.getLogger(__name__)


class sale_order(models.Model):
    _inherit = 'sale.order'

    amount_delivery_taxed = fields.Float(
        compute='get_amount_delivery_taxed',
        string='Delivery Amount With Tax',
        digits=dp.get_precision('Account'),
    )

    @api.one
    def get_amount_delivery_taxed(self):
        amount_delivery_taxed = 0.0
        for line in self.order_line.filtered('is_delivery'):
            amount_delivery_taxed += line.tax_id.compute_all(
                line.price_subtotal, product=line.product_id,
                partner=self.partner_id)['total_included']
        self.amount_delivery_taxed = amount_delivery_taxed
