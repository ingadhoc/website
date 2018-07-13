##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields, api, _
from odoo.addons.payment.models.payment_acquirer import ValidationError


class SaleOrder(models.Model):

    _inherit = 'sale.order'

    todopago_max_installments = fields.Integer(
        copy=False,
        help='If no value is configured here, then default todopago value is '
        'going to be used.',
    )

    @api.constrains('todopago_max_installments')
    def _check_todopago_max_installments(self):

        max_installments = 12
        # TODO K: move as parameter of the system.

        out_of_range = self.filtered(
            lambda x: x.todopago_max_installments and
            not 0 <= x.todopago_max_installments <= max_installments
        )
        if out_of_range:
            raise ValidationError(_(
                'Max installments must be between 0 and %s' % max_installments
            ))
