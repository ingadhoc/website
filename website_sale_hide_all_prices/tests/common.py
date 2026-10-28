from odoo import http
from odoo.addons.website_sale.models.website import CART_SESSION_CACHE_KEY
from odoo.addons.website_sale.tests.common import WebsiteSaleCommon
from odoo.fields import Command
from odoo.http import root
from odoo.tests import HttpCase


class HideAllPricesHttpCommon(WebsiteSaleCommon, HttpCase):
    """Shared scenario for the eCommerce flows: a product with a price that
    cannot match any other figure on the page, and helpers to drive a cart
    through the public session."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Distinctive price, so its presence in the HTML only comes from this product
        cls.priced_product = cls._create_product(name="Hidden Price Product", list_price=4321.0)
        cls.price_text = "4,321.00"
        cls.partner.write(dict(cls.dummy_partner_address_values, name="Hide Prices Customer"))

    def _set_hide_all_prices(self, hide):
        self.website.website_hide_all_prices = hide

    def _create_cart(self, partner=None):
        return self.env["sale.order"].create(
            {
                "partner_id": (partner or self.partner).id,
                "website_id": self.website.id,
                "order_line": [Command.create({"product_id": self.priced_product.id})],
            }
        )

    def _start_session(self, cart, login=None):
        # Bind the cart to a fresh public (or logged) session, as the shop does
        session = self.authenticate(login, login)
        session[CART_SESSION_CACHE_KEY] = cart.id
        root.session_store.save(session)
        return session

    def _reload_session(self, session):
        return root.session_store.get(session.sid)

    def _csrf(self):
        return http.Request.csrf_token(self)
