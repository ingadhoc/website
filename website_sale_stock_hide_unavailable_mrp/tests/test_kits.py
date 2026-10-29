from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestHideUnavailableKits(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        cls.warehouse = cls.env["stock.warehouse"].search([("company_id", "=", cls.company.id)], limit=1)
        cls.website = cls.env["website"].create(
            {
                "name": "Kit shop",
                "company_id": cls.company.id,
                "warehouse_id": cls.warehouse.id,
                "out_of_stock_display": "hide",
            }
        )

    def _product(self, name, published=True):
        return self.env["product.template"].create(
            {
                "name": name,
                "type": "consu",
                "is_storable": True,
                "allow_out_of_stock_order": False,
                "is_published": published,
            }
        )

    def _kit(self, name, components):
        kit = self._product(name)
        self.env["mrp.bom"].create(
            {
                "product_tmpl_id": kit.id,
                "type": "phantom",
                "bom_line_ids": [
                    (0, 0, {"product_id": component.product_variant_id.id, "product_qty": 1})
                    for component in components
                ],
            }
        )
        return kit

    def _queued(self):
        return self.env["product.template.stock.dirty"].search([]).product_tmpl_id

    def test_component_stock_enqueues_its_kit(self):
        component = self._product("Component")
        kit = self._kit("Kit", component)
        self.env["product.template.stock.dirty"].search([]).unlink()
        self.env["stock.quant"]._update_available_quantity(component.product_variant_id, self.warehouse.lot_stock_id, 3)
        self.assertIn(kit, self._queued(), "the kit's availability comes from its components")

    def test_nested_kits_are_enqueued_too(self):
        component = self._product("Deep component")
        inner = self._kit("Inner kit", component)
        outer = self._kit("Outer kit", inner)
        self.env["product.template.stock.dirty"].search([]).unlink()
        self.env["stock.quant"]._update_available_quantity(component.product_variant_id, self.warehouse.lot_stock_id, 3)
        queued = self._queued()
        self.assertIn(inner, queued)
        self.assertIn(outer, queued)

    def test_unpublished_kit_is_not_enqueued(self):
        component = self._product("Other component")
        kit = self._kit("Unpublished kit", component)
        kit.is_published = False
        self.env["product.template.stock.dirty"].search([]).unlink()
        self.env["stock.quant"]._update_available_quantity(component.product_variant_id, self.warehouse.lot_stock_id, 3)
        self.assertNotIn(kit, self._queued(), "only candidates are enqueued")
