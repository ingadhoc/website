from odoo import fields, models
from odoo.tools import is_html_empty


class ExceptionRule(models.Model):
    _inherit = "exception.rule"

    website_check = fields.Boolean(
        "Check on eCommerce",
        help="Check this rule on the eCommerce checkout, before the payment. "
        "Rules without this check are not evaluated on eCommerce orders.",
    )
    website_message = fields.Html(
        "eCommerce Message",
        translate=True,
        help="Only shown to the customer on the eCommerce, when this exception blocks the purchase. "
        "If empty, a default message is shown.",
    )

    def _get_website_messages(self):
        """Return the messages to show on the eCommerce, without duplicates."""
        default_message = self.env._("We can't process your order right now. Please contact us to continue.")
        messages = []
        for rule in self:
            message = default_message if is_html_empty(rule.website_message) else rule.website_message
            if message not in messages:
                messages.append(message)
        return messages
