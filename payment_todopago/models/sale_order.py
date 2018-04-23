##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields, api, _
from odoo.addons.payment.models.payment_acquirer import ValidationError
import logging
_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    todopago_max_insallments = fields.Integer(
        copy=False,
        help='If no value is configured here, then default todopago value is '
        'going to be used.'
    )

    @api.multi
    @api.constrains('todopago_max_insallments')
    def check_todopago_max_insallments(self):
        for rec in self:
            if rec.todopago_max_insallments and not \
                    0 <= rec.todopago_max_insallments <= 12:
                raise ValidationError(_(
                    'Max installments must be between 0 and 12'))
