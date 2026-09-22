from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestHideUnavailable(TransactionCase):
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

    def _add_variants(self, template):
        attribute = self.env["product.attribute"].create(
            {
                "name": "Color",
                "create_variant": "always",
                "value_ids": [(0, 0, {"name": "Red"}), (0, 0, {"name": "Blue"})],
            }
        )
        template.write(
            {
                "attribute_line_ids": [
                    (
                        0,
                        0,
                        {
                            "attribute_id": attribute.id,
                            "value_ids": [(6, 0, attribute.value_ids.ids)],
                        },
                    )
                ]
            }
        )

    def _shop_ids(self, website):
        return set(self.env["product.template"].search(website.sale_product_domain()).ids)

    def _rows(self, template):
        return self.env["product.template.stock.availability"].search([("product_tmpl_id", "=", template.id)])

    # -- tests --------------------------------------------------------------

    def test_hide_filters_out_of_stock(self):
        product = self._product("Out of stock")  # no stock -> free_qty 0
        self.env["website"]._recompute_stock_availability(product)
        self.assertTrue(self._rows(product), "row expected for out-of-stock product")
        self.assertNotIn(product.id, self._shop_ids(self.website))

    def test_show_keeps_out_of_stock(self):
        product = self._product("Out of stock show")
        self.website.out_of_stock_display = "hide"
        self.env["website"]._recompute_stock_availability(product)
        self.website.out_of_stock_display = "show"
        self.assertIn(product.id, self._shop_ids(self.website), "with 'show' the product must not be filtered")

    def test_allow_out_of_stock_never_hidden(self):
        product = self._product("Sellable OOS", allow_oos=True)
        self.env["website"]._recompute_stock_availability(product)
        self.assertFalse(self._rows(product))
        self.assertIn(product.id, self._shop_ids(self.website))

    def test_in_stock_is_visible(self):
        product = self._product("In stock")
        self._set_stock(product, self.wh_a, 7)
        self.env["website"]._recompute_stock_availability(product)
        self.assertFalse(self._rows(product))
        self.assertIn(product.id, self._shop_ids(self.website))

    def test_variant_product_not_hidden(self):
        product = self._product("Has variants")
        self._add_variants(product)
        self.assertGreater(product.product_variant_count, 1)
        self.env["website"]._recompute_stock_availability(product)
        self.assertFalse(self._rows(product), "multi-variant is out of scope")
        self.assertIn(product.id, self._shop_ids(self.website))

    def test_reappears_when_gains_variants(self):
        product = self._product("Becomes variant")
        self.env["website"]._recompute_stock_availability(product)
        self.assertTrue(self._rows(product))
        self._add_variants(product)
        self.env["website"]._recompute_stock_availability(product)
        self.assertFalse(self._rows(product), "rows must be cleared once multi-variant")
        self.assertIn(product.id, self._shop_ids(self.website))

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
        # stock in any company warehouse must make it visible company-wide
        self._set_stock(product, self.wh_b, 3)
        self.env["website"]._recompute_stock_availability(product)
        self.assertFalse(
            self._rows(product).filtered(lambda r: not r.warehouse_id),
            "company-wide scope should see stock from any warehouse",
        )
        self.assertIn(product.id, self._shop_ids(website))

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

    def test_drain_cron_roundtrip(self):
        product = self._product("Roundtrip")
        self.env["product.template.stock.dirty"].search([]).unlink()
        product._enqueue_stock_availability()
        self.env["website"]._cron_drain_stock_availability()
        self.assertTrue(self._rows(product))
        self.assertFalse(self.env["product.template.stock.dirty"].search([]))
        # restock -> hook enqueues -> drain removes the row
        self._set_stock(product, self.wh_a, 4)
        self.env["website"]._cron_drain_stock_availability()
        self.assertFalse(self._rows(product))
        self.assertIn(product.id, self._shop_ids(self.website))

    def test_public_user_filter_without_acl(self):
        # The filter must resolve for a public shopper even though public users
        # have no ACL on the availability table (bypass_search_access).
        product = self._product("Public hidden")
        self.env["website"]._recompute_stock_availability(product)
        public = self.env.ref("base.public_user")
        ids = self.env["product.template"].with_user(public).search(self.website.sale_product_domain()).ids
        self.assertNotIn(product.id, ids)

    def test_ordering_last_helper(self):
        self.website.out_of_stock_display = "last"
        out = self._product("Last one")
        keep = self._product("Keep")
        self._set_stock(keep, self.wh_a, 2)
        self.env["website"]._recompute_stock_availability(out + keep)
        unavailable = self.website._get_unavailable_tmpl_ids(out + keep)
        self.assertEqual(unavailable, {out.id})
        ordered = (out + keep).sorted(key=lambda p: p.id in unavailable)
        self.assertEqual(ordered[-1], out, "out-of-stock product goes last")
