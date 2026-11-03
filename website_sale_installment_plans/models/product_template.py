from odoo import models
from odoo.http import request


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def _get_published_installments(self):
        # Searched once per HTTP request: the shop grid asks for every product.
        # Keyed by cursor, a read-only request may be retried on a new one.
        cache = getattr(request, "_website_installment_plans", None) if request else None
        if cache and cache[0] is self.env.cr:
            return cache[1]
        company = self.env.website.company_id or self.env.company
        installments = (
            self.env["account.card.installment"]
            .sudo()
            .search(
                [
                    ("is_published", "=", True),
                    ("card_id.active", "=", True),
                    ("card_id.company_id", "in", [False, *company.parent_ids.ids]),
                ],
                order="divisor, id",
            )
        )
        if request:
            request._website_installment_plans = (self.env.cr, installments)
        return installments

    def _get_installment_plans(self, price):
        if not price:
            return []
        currency = self.env.website.currency_id or self.env.company.currency_id
        plans = []
        for plan in self._get_published_installments():
            values = plan.map_installment_values(price, currency=currency)
            count = 1 if (plan.divisor or 1) == 1 else plan.installment or 1
            plans.append(
                {
                    "count": count,
                    "amount": values["amount"] / count,
                    "total": values["amount"],
                    "description": values["description"],
                    "message": plan.message or "",
                }
            )
        return plans
