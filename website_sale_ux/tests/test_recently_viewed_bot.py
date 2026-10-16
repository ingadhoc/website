from odoo.tests import HttpCase, tagged

BOT_UA = "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
BROWSER_UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"


@tagged("post_install", "-at_install")
class TestRecentlyViewedBot(HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env["product.product"].create({"name": "Test Product", "type": "consu", "is_published": True})

    def _view_product(self, user_agent):
        self.make_jsonrpc_request(
            "/shop/products/recently_viewed_update",
            {"product_id": self.product.id},
            headers={"User-Agent": user_agent},
        )

    def test_bot_does_not_create_visitor(self):
        visitors = self.env["website.visitor"].search_count([])
        self._view_product(BOT_UA)
        self.assertEqual(self.env["website.visitor"].search_count([]), visitors)

    def test_browser_creates_visitor(self):
        visitors = self.env["website.visitor"].search_count([])
        self._view_product(BROWSER_UA)
        self.assertEqual(self.env["website.visitor"].search_count([]), visitors + 1)
