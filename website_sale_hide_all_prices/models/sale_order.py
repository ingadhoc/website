from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _send_payment_succeeded_for_order_mail(self):
        """Prevent sending a mail to the SO customer if the module is installed.

        :return: None
        """

        for order in self:
            if order.website_id and order.website_id.website_hide_all_prices:
                return

        return super()._send_payment_succeeded_for_order_mail()
