##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo.tests import HttpCase, tagged


@tagged("post_install", "-at_install")
class TestCartOffcanvas(HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.website = cls.env.ref("website.default_website")
        cls.website.add_to_cart_action = "open_offcanvas"

        cls.product = cls.env["product.template"].create(
            {
                "name": "Offcanvas Product",
                "type": "consu",
                "list_price": 100.0,
                "taxes_id": False,
                "is_published": True,
            }
        )
        optional_product = cls.env["product.template"].create(
            {
                "name": "Offcanvas Option",
                "type": "consu",
                "list_price": 10.0,
                "taxes_id": False,
                "is_published": True,
            }
        )
        # An optional product is what makes the configurator dialog show up on "Add to cart".
        cls.configurable_product = cls.env["product.template"].create(
            {
                "name": "Offcanvas Configurable",
                "type": "consu",
                "list_price": 50.0,
                "taxes_id": False,
                "is_published": True,
                "optional_product_ids": [(6, 0, optional_product.ids)],
            }
        )

    def test_panel_opens_when_adding_from_the_product_page(self):
        self.start_tour("/shop", "website_sale_cart_offcanvas_add_from_product")

    def test_panel_opens_empty_from_the_header_icon(self):
        self.start_tour("/shop", "website_sale_cart_offcanvas_header_empty")

    def test_panel_closes_on_backdrop_click(self):
        self.start_tour("/shop", "website_sale_cart_offcanvas_close_on_backdrop")

    def test_panel_opens_after_the_configurator(self):
        self.start_tour("/shop", "website_sale_cart_offcanvas_configurator")

    def test_standard_notification_when_setting_is_stay(self):
        self.website.add_to_cart_action = "stay"
        self.start_tour("/shop", "website_sale_cart_offcanvas_stay")
