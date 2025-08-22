<<<<<<< HEAD
||||||| MERGE BASE
=======
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class AccountCardInstallment(models.Model):
    _name = 'account.card.installment'
    _inherit = ['account.card.installment', 'website.published.mixin']

    message = fields.Char(string='Mensaje', help='Mensaje que se muestra al final de la leyenda de cuotas')

    @api.constrains('divisor')
    def _check_divisor(self):
        for record in self:
            if record.divisor <= 0:
                raise ValidationError(_('El divisor debe ser mayor que cero.'))

    def map_installment_values(self, amount_total):
        self.ensure_one()

        result = super().map_installment_values(amount_total)

        divisor = self.divisor if self.divisor else 1
        installment = self.installment if self.installment else 1
        amount = result['amount']
        description = 'En %s cuota de $%.2f' % (divisor, amount) if divisor == 1 else 'En %s cuotas de $%.2f (Total $%.2f)' % (installment, amount / installment, amount)

        result.update({
            'description': description,
        })

        return result

>>>>>>> FORWARD PORTED
