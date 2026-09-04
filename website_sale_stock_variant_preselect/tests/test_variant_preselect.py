from odoo.addons.website_sale.tests.common import MockRequest
from odoo.addons.website_sale_stock.tests.common import WebsiteSaleStockCommon
from odoo.addons.website_sale_stock_variant_preselect.controllers.main import WebsiteSale
from odoo.fields import Command
from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestVariantPreselect(WebsiteSaleStockCommon):
    """On the product page, the default combination must be the first variant *with
    stock* in the configured attribute order, instead of core's first variant in
    sequence regardless of availability.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.website.warehouse_id = cls.warehouse

        cls.attribute = cls.env["product.attribute"].create(
            {
                "name": "Test Color",
                "create_variant": "always",
                "value_ids": [
                    Command.create({"name": "Red", "sequence": 1}),
                    Command.create({"name": "Green", "sequence": 2}),
                    Command.create({"name": "Blue", "sequence": 3}),
                ],
            }
        )
        cls.red_value, cls.green_value, cls.blue_value = cls.attribute.value_ids

        # `_create_product` builds a `product.product`; we need the template so the
        # attribute line generates the three variants.
        cls.product = cls.env["product.template"].create(
            {
                "name": "Preselect test product",
                "type": "consu",
                "is_storable": True,
                "allow_out_of_stock_order": False,
                "list_price": 100.0,
                "uom_id": cls.uom_unit.id,
                "categ_id": cls.product_category.id,
                "website_published": True,
                "attribute_line_ids": [
                    Command.create(
                        {
                            "attribute_id": cls.attribute.id,
                            "value_ids": [Command.set(cls.attribute.value_ids.ids)],
                        }
                    ),
                ],
            }
        )
        assert len(cls.product.product_variant_ids) == 3, "setup must produce three variants"
        cls.red, cls.green, cls.blue = (
            cls._variant_for(cls.red_value),
            cls._variant_for(cls.green_value),
            cls._variant_for(cls.blue_value),
        )

    @classmethod
    def _variant_for(cls, attribute_value):
        return cls.product.product_variant_ids.filtered(
            lambda variant: attribute_value in variant.product_template_attribute_value_ids.product_attribute_value_id
        )

    def _preselected_variant_id(self, product=None):
        """Return the variant the product page would preselect for `product`."""
        product = product or self.product
        env = self.env(user=self.public_user)
        with MockRequest(env, website=self.website.with_env(env)):
            combination_info = (
                product.with_env(env)
                .with_context(website_sale_preselect_available_variant=True)
                ._get_combination_info()
            )
        return combination_info["product_id"]

    def test_preselects_first_variant_with_stock(self):
        """Red is first in sequence but sold out, so Green must be preselected."""
        self._add_product_qty_to_wh(self.green.id, 10, self.warehouse.lot_stock_id.id)

        self.assertEqual(self._preselected_variant_id(), self.green.id)

    def test_respects_configured_order_not_variant_order(self):
        """With Green and Blue both in stock, the earlier one in the attribute order wins."""
        self._add_product_qty_to_wh(self.green.id, 10, self.warehouse.lot_stock_id.id)
        self._add_product_qty_to_wh(self.blue.id, 99, self.warehouse.lot_stock_id.id)

        self.assertEqual(self._preselected_variant_id(), self.green.id)

    def test_keeps_first_variant_when_it_has_stock(self):
        """Nothing changes when core's default already has stock."""
        self._add_product_qty_to_wh(self.red.id, 10, self.warehouse.lot_stock_id.id)

        self.assertEqual(self._preselected_variant_id(), self.red.id)

    def test_falls_back_when_no_variant_has_stock(self):
        """With the whole template sold out, core's behaviour is kept."""
        self.assertEqual(self._preselected_variant_id(), self.red.id)

    def test_skipped_when_out_of_stock_order_allowed(self):
        """A shop that sells out of stock never shows 'sold out', so there is nothing to fix."""
        self.product.allow_out_of_stock_order = True
        self._add_product_qty_to_wh(self.green.id, 10, self.warehouse.lot_stock_id.id)

        self.assertEqual(self._preselected_variant_id(), self.red.id)

    def test_skipped_when_not_storable(self):
        """Availability says nothing about a product whose inventory is not tracked."""
        # Stock first: Odoo refuses to create quants once the product is not storable.
        self._add_product_qty_to_wh(self.green.id, 10, self.warehouse.lot_stock_id.id)
        self.product.is_storable = False

        self.assertEqual(self._preselected_variant_id(), self.red.id)

    def test_kill_switch_turns_preselection_off(self):
        """Setting the system parameter to False restores core's behaviour."""
        self.env["ir.config_parameter"].sudo().set_param("website_sale_stock_variant_preselect.enabled", "False")
        self._add_product_qty_to_wh(self.green.id, 10, self.warehouse.lot_stock_id.id)

        self.assertEqual(self._preselected_variant_id(), self.red.id)

    def test_controller_preselects_on_product_page(self):
        """The product page controller asks for the stock-aware combination."""
        self._add_product_qty_to_wh(self.green.id, 10, self.warehouse.lot_stock_id.id)

        env = self.env(user=self.public_user)
        with MockRequest(env, website=self.website.with_env(env)):
            values = WebsiteSale()._prepare_product_values(self.product.with_env(env), False)

        self.assertEqual(values["combination_info"]["product_id"], self.green.id)

    def test_controller_respects_visitor_choice(self):
        """An explicit `attribute_values` always wins over the preselection."""
        self._add_product_qty_to_wh(self.green.id, 10, self.warehouse.lot_stock_id.id)

        env = self.env(user=self.public_user)
        with MockRequest(env, website=self.website.with_env(env)):
            values = WebsiteSale()._prepare_product_values(
                self.product.with_env(env), False, attribute_values=str(self.blue_value.id)
            )

        self.assertEqual(values["combination_info"]["product_id"], self.blue.id)
