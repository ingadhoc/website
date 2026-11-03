from odoo import fields, models
from odoo.tools import format_amount


class AccountCardInstallment(models.Model):
    _name = "account.card.installment"
    _inherit = ["account.card.installment", "website.published.mixin"]

    message = fields.Char(help="Message displayed at the end of the installment legend")

    def map_installment_values(self, amount_total, currency=None):
        self.ensure_one()

        result = super().map_installment_values(amount_total)

        currency = currency or self.card_id.company_id.currency_id or self.env.company.currency_id
        amount = result["amount"]
        if (self.divisor or 1) == 1:
            description = self.env._(
                "%(count)s installment of %(amount)s",
                count=1,
                amount=format_amount(self.env, amount, currency),
            )
        else:
            installment = self.installment or 1
            description = self.env._(
                "%(count)s installments of %(amount)s (Total %(total)s)",
                count=installment,
                amount=format_amount(self.env, amount / installment, currency),
                total=format_amount(self.env, amount, currency),
            )
        result["description"] = description
        return result
