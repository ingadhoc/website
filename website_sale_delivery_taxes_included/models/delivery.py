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


class delivery_carrier(models.Model):
    _inherit = 'delivery.carrier'

    taxed_price = fields.Float(
        compute='get_taxed_price',
        string='Taxed Price',
        digits=dp.get_precision('Account'),
        )

    @api.one
    def get_taxed_price(self):
        for carrier in self:
            company_id = (
                self._context.get('company_id') or
                self.env.user.company_id.id)
            taxed_price = \
                carrier.product_id.taxes_id.filtered(
                    lambda x: x.company_id.id == company_id).compute_all(
                    carrier.price, 1.0,
                    product=carrier.product_id)['total_included']
            self.taxed_price = taxed_price
