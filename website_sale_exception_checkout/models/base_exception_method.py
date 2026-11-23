from odoo import models


class BaseExceptionMethod(models.AbstractModel):
    _inherit = "base.exception.method"

    def _rule_domain(self):
        domain = super()._rule_domain()
        if self._name in ("sale.order", "sale.order.line"):
            orders = self._get_main_records()
            if orders and all(order.website_id for order in orders):
                # tuples, not lists: the domain is used as an ormcache key
                domain = domain + [("website_check", "=", True)]
        return domain
