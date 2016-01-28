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
                line.price_subtotal, 1.0, product=line.product_id,
                partner=self.partner_id)['total_included']
        self.amount_delivery_taxed = amount_delivery_taxed


class sale_order_line(models.Model):
    _inherit = 'sale.order.line'

    # we overwrite this field to add taxes or not regarding company
    # configuration
    discounted_price = fields.Float(
        compute='_fnct_get_discounted_price',
        string='Discounted price',
        digits=dp.get_precision('Product Price')
        )

    @api.multi
    def _fnct_get_discounted_price(self):
        # TODO add company condition to include or not
        # TODO perhups we can use l10n_ar_sale printed prices
        for line in self:
            discounted_price = (
                line.price_unit * (1.0 - (line.discount or 0.0) / 100.0))
            # add taxes
            discounted_price = line.tax_id.compute_all(
                discounted_price, 1.0, product=line.product_id,
                partner=line.order_id.partner_id)['total_included']
            line.discounted_price = discounted_price
