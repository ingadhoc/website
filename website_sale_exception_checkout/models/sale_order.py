from odoo import models
from odoo.exceptions import ValidationError
from odoo.tools import html2plaintext


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _get_website_exceptions(self):
        """Return the eCommerce exception rules that apply to the order.

        Uses _get_exceptions instead of detect_exceptions, so nothing is raised
        and the exceptions are not stored on the order (sale_exception still
        stores them on the lines).
        """
        self.ensure_one()
        rule_ids = self._get_exceptions()[0] + self.order_line._get_exceptions()[0]
        return self.env["exception.rule"].sudo().browse(list(dict.fromkeys(rule_ids)))

    def _check_cart_is_ready_to_be_paid(self):
        res = super()._check_cart_is_ready_to_be_paid()
        exceptions = self._get_website_exceptions()
        if exceptions:
            raise ValidationError("\n".join(html2plaintext(message) for message in exceptions._get_website_messages()))
        return res
