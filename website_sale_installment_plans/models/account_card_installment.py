from odoo import _, fields, models


class AccountCardInstallment(models.Model):
    _name = "account.card.installment"
    _inherit = ["account.card.installment", "website.published.mixin"]

    message = fields.Char(help="Message displayed at the end of the installment legend")

    def map_installment_values(self, amount_total):
        self.ensure_one()

        result = super().map_installment_values(amount_total)

        divisor = self.divisor if self.divisor else 1
        installment = self.installment if self.installment else 1
        amount = result["amount"]
        description = (
            _("%s installment of $%.2f") % (divisor, amount)
            if divisor == 1
            else _("%s installments of $%.2f (Total $%.2f)") % (installment, amount / installment, amount)
        )

        result.update(
            {
                "description": description,
            }
        )

        return result
