from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestHideUnavailableWithInventory(TransactionCase):
    """What only exists with Inventory: the website warehouse and the quants."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        cls.wh_a = cls.env["stock.warehouse"].search([("company_id", "=", cls.company.id)], limit=1)
        cls.wh_b = cls.env["stock.warehouse"].create({"name": "WH B", "code": "WHB", "company_id": cls.company.id})
        cls.website = cls.env["website"].create(
            {
                "name": "Shop A",
                "company_id": cls.company.id,
                "warehouse_id": cls.wh_a.id,
                "out_of_stock_display": "hide",
            }
        )

    # -- helpers ------------------------------------------------------------

    def _product(self, name, allow_oos=False, published=True):
        return self.env["product.template"].create(
            {
                "name": name,
                "type": "consu",
                "is_storable": True,
                "allow_out_of_stock_order": allow_oos,
                "is_published": published,
            }
        )

    def _set_stock(self, template, warehouse, qty):
        self.env["stock.quant"]._update_available_quantity(template.product_variant_id, warehouse.lot_stock_id, qty)

    def _shop_ids(self, website):
        return set(self.env["product.template"].search(website.sale_product_domain()).ids)

    def _rows(self, template):
        return self.env["product.template.stock.availability"].search([("product_tmpl_id", "=", template.id)])

    # -- tests --------------------------------------------------------------

    def test_blank_warehouse_resolves_company_wide(self):
        website = self.env["website"].create(
            {
                "name": "Shop company",
                "company_id": self.company.id,
                "warehouse_id": False,
                "out_of_stock_display": "hide",
            }
        )
        product = self._product("Company scope")
        # Stock in any warehouse of the company counts for a website that has
        # none set: the core resolves availability company-wide.
        self._set_stock(product, self.wh_b, 3)
        self.env["website"]._recompute_stock_availability(product)
        self.assertFalse(
            self._rows(product).filtered(lambda row: row.website_id == website),
            "a website without a warehouse sees stock from any of them",
        )
        self.assertIn(product.id, self._shop_ids(website))

    def test_changing_the_warehouse_reconciles_the_website(self):
        # The warehouse is what this website measures availability against, so
        # changing it changes every answer.
        product = self._product("Warehouse switch")
        self._set_stock(product, self.wh_b, 7)
        self.env["website"]._recompute_stock_availability(product)
        self.assertTrue(self._rows(product), "no stock in WH A")

        self.website.warehouse_id = self.wh_b
        self.env["website"]._cron_full_sweep_stock_availability()
        self.assertFalse(self._rows(product), "there is stock in WH B")

    def test_two_websites_distinct_warehouses(self):
        website_b = self.env["website"].create(
            {
                "name": "Shop B",
                "company_id": self.company.id,
                "warehouse_id": self.wh_b.id,
                "out_of_stock_display": "hide",
            }
        )
        product = self._product("Only in A")
        self._set_stock(product, self.wh_a, 5)  # stock in A, none in B
        self.env["website"]._recompute_stock_availability(product)
        self.assertIn(product.id, self._shop_ids(self.website), "visible in A")
        self.assertNotIn(product.id, self._shop_ids(website_b), "hidden in B")

    def test_quant_hook_enqueues_only_candidates(self):
        candidate = self._product("Candidate")
        sellable = self._product("Sellable", allow_oos=True)
        self.env["product.template.stock.dirty"].search([]).unlink()
        self._set_stock(candidate, self.wh_a, 1)
        self._set_stock(sellable, self.wh_a, 1)
        queued = self.env["product.template.stock.dirty"].search([]).product_tmpl_id
        self.assertIn(candidate, queued)
        self.assertNotIn(sellable, queued)
