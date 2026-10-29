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

    def _set_stock(self, template, qty):
        self.env["stock.quant"]._update_available_quantity(
            template.product_variant_id, self.warehouse.lot_stock_id, qty
        )

    def _rows(self, template):
        return self.env["product.template.stock.availability"].search([("product_tmpl_id", "=", template.id)])

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

    def test_changing_the_bom_enqueues_the_kit(self):
        # What a kit can ship depends on its bill, not only on stock moves.
        component = self._product("Bill component")
        kit = self._kit("Bill kit", component)
        bom = self.env["mrp.bom"].search([("product_tmpl_id", "=", kit.id)], limit=1)
        other = self._product("Second component")
        self.env["product.template.stock.dirty"].search([]).unlink()
        self.env["mrp.bom.line"].create({"bom_id": bom.id, "product_id": other.product_variant_id.id, "product_qty": 1})
        self.assertIn(kit, self._queued(), "a new component changes what the kit can ship")

    def test_dropping_the_bom_enqueues_the_kit(self):
        component = self._product("Dropped component")
        kit = self._kit("Dropped kit", component)
        bom = self.env["mrp.bom"].search([("product_tmpl_id", "=", kit.id)], limit=1)
        self.env["product.template.stock.dirty"].search([]).unlink()
        bom.unlink()
        self.assertIn(kit, self._queued(), "without its bill the product is no longer a kit")

    def test_kit_is_hidden_when_its_components_run_out(self):
        # The queue is only half the claim: the kit has to end up hidden.
        component = self._product("Stocked component")
        kit = self._kit("Stocked kit", component)
        self.env["website"]._recompute_stock_availability(kit)
        self.assertTrue(self._rows(kit), "a kit without component stock is unavailable")
        self.assertNotIn(kit.id, self.env["product.template"].search(self.website.sale_product_domain()).ids)
        self._set_stock(component, 10)
        # free_qty of a kit comes from its components through mrp; in one
        # transaction the cached value does not follow the component's quant.
        self.env.invalidate_all()
        self.env["website"]._recompute_stock_availability(kit)
        self.assertFalse(self._rows(kit), "stock on the component makes the kit available again")
        self.assertIn(kit.id, self.env["product.template"].search(self.website.sale_product_domain()).ids)
