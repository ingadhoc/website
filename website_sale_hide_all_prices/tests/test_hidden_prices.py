from lxml import html
from odoo.tests import new_test_user, tagged

from .common import HideAllPricesHttpCommon


@tagged("post_install", "-at_install")
class TestHiddenPrices(HideAllPricesHttpCommon):
    """With 'hide all prices' on, no eCommerce page shows the product price, and
    the frontend session tells the JS to hide it too. With the setting off every
    page shows the price, which proves each check looks at the right place.

    Declared, not tested: what the JS hides on its own (extra price badges in the
    product configurator, the price in the 'added to cart' notification and the
    comparison row) needs a tour."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.portal_user = new_test_user(cls.env, login="hide_prices_portal", groups="base.group_portal")
        cls.portal_user.partner_id.write(dict(cls.dummy_partner_address_values, name="Hide Prices Portal"))
        cls.env["product.wishlist"].create(
            {
                "partner_id": cls.portal_user.partner_id.id,
                "product_id": cls.priced_product.product_variant_id.id,
                "website_id": cls.website.id,
                "pricelist_id": cls.pricelist.id,
            }
        )

    def _page(self, url):
        response = self.url_open(url)
        self.assertEqual(response.status_code, 200, url)
        return response.text

    def test_prices_hidden_on_every_shop_page(self):
        variant = self.priced_product.product_variant_id
        for hide in (False, True):
            self._set_hide_all_prices(hide)
            state = "on" if hide else "off"
            assert_price = self.assertNotIn if hide else self.assertIn

            # Anonymous pages
            self._start_session(self._create_cart())
            with self.subTest("shop grid, hide all prices %s" % state):
                assert_price(self.price_text, self._page("/shop?search=Hidden Price Product"))
            with self.subTest("product page, hide all prices %s" % state):
                assert_price(self.price_text, self._page(self.priced_product.website_url))
            with self.subTest("comparison page, hide all prices %s" % state):
                assert_price(self.price_text, self._page("/shop/compare?products=%s" % variant.id))
            with self.subTest("cart, hide all prices %s" % state):
                assert_price(self.price_text, self._page("/shop/cart"))
            with self.subTest("checkout summary, hide all prices %s" % state):
                checkout = self._page("/shop/checkout")
                assert_price(self.price_text, checkout)
                # The delivery form stays in the DOM but hidden
                delivery_form = html.fromstring(checkout).get_element_by_id("o_delivery_form")
                (self.assertIn if hide else self.assertNotIn)("d-none", delivery_form.get("class", "").split())
            with self.subTest("frontend session flag, hide all prices %s" % state):
                self.assertIn('"website_hide_all_prices": %s' % ("true" if hide else "false"), self._page("/shop"))

            # The wishlist needs a logged customer
            self.authenticate(self.portal_user.login, self.portal_user.login)
            with self.subTest("wishlist, hide all prices %s" % state):
                # The wishlist price stays in the DOM but hidden; nowhere else shows it
                tree = html.fromstring(self._page("/shop/wishlist"))
                wish_prices = tree.find_class("o_wish_price")
                self.assertTrue(wish_prices)
                for wish_price in wish_prices:
                    (self.assertIn if hide else self.assertNotIn)("d-none", wish_price.get("class").split())
                    if not hide:
                        self.assertIn(self.price_text, wish_price.text_content())
                    wish_price.drop_tree()
                if hide:
                    self.assertNotIn(self.price_text, html.tostring(tree, encoding="unicode"))
