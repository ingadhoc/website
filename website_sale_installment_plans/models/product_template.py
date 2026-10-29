from odoo import models
from odoo.http import request
from odoo.tools import format_amount


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
            amount = plan.map_installment_values(price)["amount"]
            if (plan.divisor or 1) == 1:
                count, total = 1, amount
                description = self.env._(
                    "%(count)s installment of %(amount)s",
                    count=count,
                    amount=format_amount(self.env, amount, currency),
                )
            else:
                count = plan.installment or 1
                total = amount
                description = self.env._(
                    "%(count)s installments of %(amount)s (Total %(total)s)",
                    count=count,
                    amount=format_amount(self.env, amount / count, currency),
                    total=format_amount(self.env, total, currency),
                )
            plans.append(
                {
                    "count": count,
                    "amount": amount / count,
                    "total": total,
                    "description": description,
                    "message": plan.message or "",
                }
            )
        return plans
