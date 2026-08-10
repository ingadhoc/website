from odoo import fields
from odoo.addons.website_sale.tests.common import MockRequest, WebsiteSaleCommon
from odoo.addons.website_sale_pricelist_hide_strikethrough_price.controllers.product_configurator import (
    WebsiteSaleProductConfigurator,
)
from odoo.fields import Command
from odoo.tests import HttpCase, tagged


@tagged("post_install", "-at_install")
class TestHideStrikethroughPrice(WebsiteSaleCommon):
    """The boolean `website_hide_strikethrough_price` on the active pricelist must
    neutralize, server-side, both strikethrough sources in the eCommerce:

    * the discount strikethrough (``has_discounted_price`` / ``list_price`` on the
      product page and ``base_price`` on the /shop grid), and
    * the manual compare-at price (``compare_list_price``).
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Enable the "Comparison price" feature so `compare_list_price` is exposed.
        cls.env["res.config.settings"].create({"group_product_price_comparison": True}).execute()

        # Product used for the discount-strikethrough path.
        cls.product_discount = cls.env["product.template"].create(
            {
                "name": "Discount strikethrough product",
                "list_price": 100.0,
                "website_published": True,
            }
        )
        # Product used for the compare-at price path.
        cls.product_compare = cls.env["product.template"].create(
            {
                "name": "Compare strikethrough product",
                "list_price": 100.0,
                "compare_list_price": 150.0,
                "website_published": True,
            }
        )

        def discount_item():
            return [Command.create({"compute_price": "percentage", "percent_price": 10})]

        def make_pl(name, hide, items=None):
            return cls.env["product.pricelist"].create(
                {
                    "name": name,
                    "website_id": cls.website.id,
                    "currency_id": cls.website.currency_id.id,
                    "item_ids": items or [],
                    "website_hide_strikethrough_price": hide,
                }
            )

        cls.pl_discount_show = make_pl("discount show", False, discount_item())
        cls.pl_discount_hide = make_pl("discount hide", True, discount_item())
        cls.pl_plain_show = make_pl("plain show", False)
        cls.pl_plain_hide = make_pl("plain hide", True)

        cls.cart_partner = cls.env["res.partner"].create({"name": "Cart tester"})

    def _combination_info(self, product, pricelist):
        with MockRequest(self.env, website=self.website, website_sale_current_pl=pricelist.id):
            return product._get_combination_info()

    def _sales_prices(self, product, pricelist):
        with MockRequest(self.env, website=self.website, website_sale_current_pl=pricelist.id):
            return product._get_sales_prices(self.website)[product.id]

    # --- discount strikethrough --------------------------------------------

    def test_discount_control_shows_strikethrough(self):
        """Sanity: without the flag the discount strikethrough data is present."""
        ci = self._combination_info(self.product_discount, self.pl_discount_show)
        self.assertTrue(ci["has_discounted_price"])
        self.assertGreater(ci["list_price"], ci["price"])
        sp = self._sales_prices(self.product_discount, self.pl_discount_show)
        self.assertIn("base_price", sp)
        self.assertGreater(sp["base_price"], sp["price_reduce"])

    def test_discount_hidden_by_flag(self):
        ci = self._combination_info(self.product_discount, self.pl_discount_hide)
        self.assertFalse(ci["has_discounted_price"])
        self.assertEqual(ci["list_price"], ci["price"])
        self.assertNotIn("compare_list_price", ci)
        sp = self._sales_prices(self.product_discount, self.pl_discount_hide)
        self.assertNotIn("base_price", sp)

    # --- compare-at price ---------------------------------------------------

    def test_compare_control_shows_price(self):
        """Sanity: without the flag the compare-at price is present."""
        ci = self._combination_info(self.product_compare, self.pl_plain_show)
        self.assertFalse(ci["has_discounted_price"])
        self.assertIn("compare_list_price", ci)
        self.assertGreater(ci["compare_list_price"], ci["price"])
        sp = self._sales_prices(self.product_compare, self.pl_plain_show)
        self.assertIn("base_price", sp)

    def test_compare_hidden_by_flag(self):
        ci = self._combination_info(self.product_compare, self.pl_plain_hide)
        self.assertNotIn("compare_list_price", ci)
        sp = self._sales_prices(self.product_compare, self.pl_plain_hide)
        self.assertNotIn("base_price", sp)

    # --- cart / order summary line ------------------------------------------

    def _cart_line(self, pricelist):
        order = self.env["sale.order"].create(
            {
                "partner_id": self.cart_partner.id,
                "website_id": self.website.id,
                "pricelist_id": pricelist.id,
            }
        )
        line = self.env["sale.order.line"].create(
            {
                "order_id": order.id,
                "product_id": self.product_discount.product_variant_ids[:1].id,
                "product_uom_qty": 1.0,
            }
        )
        line.discount = 10.0
        return line

    def test_cart_control_shows_strikethrough(self):
        """Sanity: without the flag the cart line shows the strikethrough."""
        line = self._cart_line(self.pl_discount_show)
        self.assertTrue(line._should_show_strikethrough_price())

    def test_cart_strikethrough_hidden_by_flag(self):
        line = self._cart_line(self.pl_discount_hide)
        self.assertFalse(line._should_show_strikethrough_price())

    # --- product / combo configurator dialog --------------------------------

    def _configurator_strikethrough(self, pricelist):
        controller = WebsiteSaleProductConfigurator()
        product = self.product_discount.product_variant_ids[:1]
        currency = self.website.currency_id
        date = fields.Date.context_today(product)
        with MockRequest(self.env, website=self.website, website_sale_current_pl=pricelist.id):
            price, rule_id = pricelist._get_product_price_rule(product, quantity=1.0, currency=currency, date=date)
            return controller._get_strikethrough_price(product, currency, date, price, rule_id)

    def test_configurator_control_shows_strikethrough(self):
        """Sanity: without the flag the configurator returns a strikethrough price."""
        st = self._configurator_strikethrough(self.pl_discount_show)
        self.assertTrue(st)

    def test_configurator_strikethrough_hidden_by_flag(self):
        self.assertIsNone(self._configurator_strikethrough(self.pl_discount_hide))


@tagged("post_install", "-at_install")
class TestHideStrikethroughWrapClass(HttpCase):
    """The frontend wrapper gets the CSS-gating class only when the visitor's
    active pricelist requests hiding the strikethrough. This is the robust net
    for cart lines whose `<del>` is forced by `website_sale_product_pack`.
    """

    def _setup(self, hide):
        website = self.env["website"].search([], limit=1)
        pl = self.env["product.pricelist"].create(
            {
                "name": "wrap %s" % hide,
                "website_id": website.id,
                "selectable": True,
                "website_hide_strikethrough_price": hide,
            }
        )
        website.user_id.partner_id.property_product_pricelist = pl
        return website

    def test_wrap_class_present_with_flag(self):
        self._setup(True)
        res = self.url_open("/shop")
        self.assertEqual(res.status_code, 200)
        self.assertIn("o_wsale_hide_strikethrough_price", res.text)

    def test_wrap_class_absent_without_flag(self):
        self._setup(False)
        res = self.url_open("/shop")
        self.assertEqual(res.status_code, 200)
        self.assertNotIn("o_wsale_hide_strikethrough_price", res.text)
