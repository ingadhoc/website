from odoo.addons.website_sale.tests.common import WebsiteSaleCommon
from odoo.addons.website_sale_exception_checkout.controllers.main import WebsiteSaleExceptionCheckout
from odoo.exceptions import ValidationError
from odoo.fields import Command
from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestWebsiteSaleExceptionCheckout(WebsiteSaleCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.controller = WebsiteSaleExceptionCheckout()
        # only services, so the native delivery check does not add errors
        cls.order = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "website_id": cls.website.id,
                "order_line": [Command.create({"product_id": cls.service_product.id, "product_uom_qty": 3})],
            }
        )
        cls.rule = cls.env["exception.rule"].create(
            {
                "name": "Amount over 100",
                "model": "sale.order",
                "exception_type": "by_domain",
                "domain": "[('amount_untaxed', '>', 100)]",
                "website_check": True,
                "website_message": "<p>Call us to finish your purchase.</p>",
            }
        )

    def test_checkout_blocked_by_website_rule(self):
        errors = self.controller._get_shop_payment_errors(self.order)
        self.assertEqual(len(errors), 1)
        self.assertIn("Call us to finish your purchase.", errors[0][1])
        with self.assertRaisesRegex(ValidationError, "Call us to finish your purchase."):
            self.order._check_cart_is_ready_to_be_paid()

    def test_exceptions_not_stored_on_checkout(self):
        self.controller._get_shop_payment_errors(self.order)
        self.assertFalse(self.order.exception_ids)

    def test_default_message(self):
        self.rule.website_message = False
        errors = self.controller._get_shop_payment_errors(self.order)
        self.assertEqual(len(errors), 1)
        self.assertIn("Please contact us to continue.", errors[0][1])

    def test_rule_without_website_check(self):
        self.rule.website_check = False
        self.assertEqual(self.controller._get_shop_payment_errors(self.order), [])
        self.order._check_cart_is_ready_to_be_paid()
        self.assertNotIn(self.rule.id, self.order._get_exceptions()[0])

    def test_backend_order_checks_every_rule(self):
        self.rule.website_check = False
        backend_order = self.order.copy({"website_id": False})
        self.assertIn(self.rule.id, backend_order._get_exceptions()[0])

    def test_order_without_exceptions(self):
        self.order.order_line.product_uom_qty = 1
        self.assertEqual(self.controller._get_shop_payment_errors(self.order), [])
        self.order._check_cart_is_ready_to_be_paid()

    def test_checkout_blocked_by_line_rule(self):
        self.rule.write(
            {
                "model": "sale.order.line",
                "domain": "[('product_uom_qty', '>', 2)]",
            }
        )
        errors = self.controller._get_shop_payment_errors(self.order)
        self.assertEqual(len(errors), 1)
        self.assertIn("Call us to finish your purchase.", errors[0][1])
