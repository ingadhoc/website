from unittest.mock import patch

from odoo.addons.website_sale.tests.common import WebsiteSaleCommon
from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestPaymentMail(WebsiteSaleCommon):
    def test_payment_mail_skipped_when_prices_are_hidden(self):
        """A website that hides all prices does not send the 'payment succeeded'
        mail to the customer; with the setting off the mail goes out.

        Declared, not tested: in a batch with orders of two websites, one hiding
        prices, today no order gets the mail. That is a bug (loa, 27/10) and is
        fixed apart, so this test does not freeze it."""
        order = self._create_so()
        sale_order_cls = self.env.registry["sale.order"]
        for hide, expected_calls in ((False, 1), (True, 0)):
            with self.subTest("payment mail with hide all prices %s" % ("on" if hide else "off")):
                self.website.website_hide_all_prices = hide
                # Only the downstream sender is mocked, the override under test runs
                with patch.object(sale_order_cls, "_send_order_notification_mail", autospec=True) as send:
                    order._send_payment_succeeded_for_order_mail()
                self.assertEqual(send.call_count, expected_calls)
