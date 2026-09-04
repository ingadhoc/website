from odoo.addons.website_sale.tests.common import MockRequest
from odoo.addons.website_sale_stock_variant_preselect.tests.common import VariantPreselectCommon
from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestOutOfStockRibbon(VariantPreselectCommon):
    """The shop grid must not label a card "Out of stock" when the template still has a
    variant that can be sold.

    Core evaluates the ribbon against the single variant the grid picked with
    `_get_first_possible_variant_id`, which ignores stock, so a template whose first
    variant is sold out gets the label even though the product page it links to opens on
    a variant that has stock.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # The ribbon record ships in `website_sale` data but with the default
        # `assign='manual'`; only `website_sale_stock`'s *demo* data turns it into the
        # automatic out-of-stock one. Reuse it rather than create a second one: core
        # allows a single ribbon per non-manual `assign` (`_check_assign`), so creating
        # another would fail on a base that has demo data.
        cls.ribbon = cls.env.ref("website_sale.out_of_stock_ribbon")
        cls.ribbon.assign = "out_of_stock"

    def _grid_variant(self, template=None):
        """Return the variant the shop grid would display for `template`."""
        template = template or self.product
        return self.env["product.product"].browse(template._get_first_possible_variant_id())

    def _ribbon_applies(self, template=None):
        template = template or self.product
        env = self.env(user=self.public_user)
        with MockRequest(env, website=self.website.with_env(env)):
            return self.ribbon.with_env(env)._is_applicable_for(self._grid_variant(template).with_env(env), {})

    def test_hidden_when_another_variant_has_stock(self):
        """Red is first and sold out, but Green can be sold: no label."""
        self._add_product_qty_to_wh(self.green.id, 10, self.warehouse.lot_stock_id.id)

        self.assertEqual(self._grid_variant(), self.red, "the grid still shows the first variant")
        self.assertFalse(self._ribbon_applies())

    def test_shown_when_no_variant_has_stock(self):
        """With the whole template sold out the label is correct and must stay."""
        self.assertTrue(self._ribbon_applies())

    def test_hidden_when_only_the_first_variant_has_stock(self):
        """The common case keeps working: core would not label it either."""
        self._add_product_qty_to_wh(self.red.id, 10, self.warehouse.lot_stock_id.id)

        self.assertFalse(self._ribbon_applies())

    def test_untouched_on_single_variant_product(self):
        """A template with one variant is core's business; we must not interfere."""
        # `_create_product` returns a `product.product`; the helpers below are on the
        # template.
        single = self._create_product(name="Single variant product").product_tmpl_id

        self.assertEqual(len(single.product_variant_ids), 1)
        self.assertTrue(self._ribbon_applies(single))

    def test_untouched_when_out_of_stock_order_allowed(self):
        """A shop selling out of stock is never sold out, with or without this module."""
        self.product.allow_out_of_stock_order = True

        self.assertFalse(self._ribbon_applies())

    def test_kill_switch_restores_core_behaviour(self):
        """With the parameter off the label comes back, wrong verdict included."""
        self.env["ir.config_parameter"].sudo().set_param("website_sale_stock_variant_preselect.enabled", "False")
        self._add_product_qty_to_wh(self.green.id, 10, self.warehouse.lot_stock_id.id)

        self.assertTrue(self._ribbon_applies())
