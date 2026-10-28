import json
from urllib.parse import urlparse

from odoo.addons.website_sale.models.website import CART_SESSION_CACHE_KEY
from odoo.tests import tagged

from .common import HideAllPricesHttpCommon


@tagged("post_install", "-at_install")
class TestQuotationCheckout(HideAllPricesHttpCommon):
    """With 'hide all prices' on, checkout ends in a quotation request instead of
    a payment: the cart is left as a draft quotation without transaction, the
    session gets a fresh cart and the customer lands on /request-quotation.
    With the setting off the native payment step is kept."""

    def _post(self, url, data):
        return self.url_open(url, data=dict(data, csrf_token=self._csrf()), allow_redirects=False)

    def _assert_redirects_to(self, response, path):
        self.assertEqual(response.status_code, 303)
        self.assertEqual(urlparse(response.headers["Location"]).path, path)

    def _assert_quotation_requested(self, cart, session):
        session = self._reload_session(session)
        self.assertEqual(cart.state, "draft")
        self.assertFalse(cart.transaction_ids)
        self.assertNotIn(CART_SESSION_CACHE_KEY, session)
        self.assertEqual(session.get("sale_last_order_id"), cart.id)

    def test_request_quotation_chain(self):
        self._set_hide_all_prices(True)
        cart = self._create_cart()
        session = self._start_session(cart)

        with self.subTest("requesting the quotation skips the payment step"):
            response = self._post("/shop/request_quotation", {})
            self._assert_redirects_to(response, "/request-quotation")
            self._assert_quotation_requested(cart, session)

        with self.subTest("the confirmation page sends back to the request page"):
            response = self.url_open("/shop/confirmation", allow_redirects=False)
            self._assert_redirects_to(response, "/request-quotation")

        with self.subTest("the 'request received' page is published"):
            response = self.url_open("/request-quotation")
            self.assertEqual(response.status_code, 200)
            self.assertIn("Your request has been sent", response.text)

    def test_request_quotation_keeps_payment_when_setting_is_off(self):
        self._set_hide_all_prices(False)
        cart = self._create_cart()
        self._start_session(cart)
        response = self._post("/shop/request_quotation", {})
        self._assert_redirects_to(response, "/shop/payment")
        self.assertEqual(cart.state, "draft")

    def test_address_submit_requests_the_quotation(self):
        self._set_hide_all_prices(True)
        address = dict(
            self.dummy_partner_address_values,
            name="Guest Customer",
            address_type="billing",
            use_delivery_as_billing="true",
        )

        with self.subTest("an invalid address keeps the native error feedback"):
            cart = self._create_cart(partner=self.public_partner)
            session = self._start_session(cart)
            feedback = json.loads(self._post("/shop/address/submit", dict(address, email="")).text)
            self.assertTrue(feedback.get("invalid_fields"))
            self.assertNotEqual(feedback.get("redirectUrl"), "/request-quotation")
            self.assertEqual(self._reload_session(session).get(CART_SESSION_CACHE_KEY), cart.id)

        with self.subTest("a saved address confirms the quotation request"):
            feedback = json.loads(self._post("/shop/address/submit", address).text)
            self.assertEqual(feedback.get("redirectUrl"), "/request-quotation")
            self._assert_quotation_requested(cart, session)
