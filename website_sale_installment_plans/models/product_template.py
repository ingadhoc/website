from odoo import models
from odoo.http import request


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def _get_published_installments(self):
        # Searched once per HTTP request: the shop grid asks for every product.
        cached = getattr(request, "_website_installment_plans", None) if request else None
        if cached is not None:
            return cached
        company = self.env.website.company_id or self.env.company
        installments = (
            self.env["account.card.installment"]
            .sudo()
            .search(
                [
                    ("is_published", "=", True),
                    ("card_id.active", "=", True),
                    ("card_id.company_id", "in", [company.id, False]),
                ],
                order="divisor, id",
            )
        )
        if request:
            request._website_installment_plans = installments
        return installments

    def _get_installment_plans(self, price):
        if not price:
            return []
        plans = []
        for plan in self._get_published_installments():
            amount = plan.map_installment_values(price)["amount"]
            count = plan.divisor or 1
            if count != 1:
                count = plan.installment or 1
            plans.append(
                {
                    "count": count,
                    "amount": amount / count,
                    "total": amount,
                    "message": plan.message or "",
                }
            )
        return plans
