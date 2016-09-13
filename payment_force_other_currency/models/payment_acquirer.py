# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, fields


class PaymentAcquirer(models.Model):
    _inherit = 'payment.acquirer'

    force_currency_id = fields.Many2one(
        'res.currency',
        'Force Currency',
        help='Use this currency instead of pricelist currency',
    )

    def render(self, cr, uid, id,
               reference, amount, currency_id,
               partner_id=False, values=None, context=None):
        # primero cambiamos la moneda porque termina haciendo un browse
        acquirer = self.browse(cr, uid, id, context=context)
        new_currency_id = False
        if acquirer.force_currency_id:
            new_currency_id = acquirer.force_currency_id.id
        partner_data, tx_data = super(
            PaymentAcquirer, self).render(
            cr, uid, id, reference, amount, new_currency_id,
            partner_id=partner_id, values=values, context=context)
        # convertimos el monto a la nueva moneda
        if new_currency_id:
            tx_data['amount'] = self.pool['res.currency'].compute(
                cr, uid, currency_id, new_currency_id, tx_data['amount'],
                context=context)
        return partner_data, tx_data
