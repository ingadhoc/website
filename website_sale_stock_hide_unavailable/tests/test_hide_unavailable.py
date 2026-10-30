from odoo import fields
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestHideUnavailable(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        cls.website = cls.env["website"].create(
            {
                "name": "Shop A",
                "company_id": cls.company.id,
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

    def _set_stock(self, template, qty):
        self._set_variant_stock(template.product_variant_id, qty)

    def _set_variant_stock(self, variant, qty):
        # Without Inventory, qty_available is a plain company-dependent column.
        variant.with_company(self.company).qty_available = qty

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

    def _snippet_filter(self):
        """A product carousel backed by an ir.filters.

        Newest first and the maximum limit the model allows, so the products
        this test creates are the ones the carousel returns.
        """
        ir_filter = self.env["ir.filters"].create(
            {
                "name": "Test products",
                "model_id": "product.product",
                "domain": "[('website_published', '=', True)]",
                "sort": '["id desc"]',
                "action_id": self.env.ref("website.action_website").id,
            }
        )
        return self.env["website.snippet.filter"].create(
            {
                "filter_id": ir_filter.id,
                "field_names": "display_name",
                "limit": 16,
                "name": "Test carousel",
            }
        )

    def _snippet_filter_server_action(self):
        """A product carousel backed by a server action, the other data source.

        The two kinds resolve their model differently, so both are covered.
        """
        action = self.env["ir.actions.server"].create(
            {
                "name": "Test products via action",
                "model_id": self.env.ref("product.model_product_product").id,
                "state": "code",
                "code": "response = env['product.product'].search(env.context.get('search_domain') or [])",
            }
        )
        return self.env["website.snippet.filter"].create(
            {
                "action_server_id": action.id,
                "field_names": "display_name",
                "limit": 16,
                "name": "Test carousel via action",
            }
        )

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
        self._set_stock(product, 7)
        self.env["website"]._recompute_stock_availability(product)
        self.assertFalse(self._rows(product))
        self.assertIn(product.id, self._shop_ids(self.website))

    def test_variants_hidden_when_every_variant_is_out(self):
        product = self._product("Has variants")
        self._add_variants(product)
        self.assertGreater(product.product_variant_count, 1)
        self.env["website"]._recompute_stock_availability(product)
        self.assertTrue(self._rows(product), "sold out when every variant is")
        self.assertNotIn(product.id, self._shop_ids(self.website))

    def test_variants_visible_when_one_has_stock(self):
        product = self._product("Partly in stock")
        self._add_variants(product)
        self._set_variant_stock(product.product_variant_ids[0], 5)
        self.env["website"]._recompute_stock_availability(product)
        self.assertFalse(self._rows(product), "one variant in stock keeps the product visible")
        self.assertIn(product.id, self._shop_ids(self.website))

    def test_stays_hidden_when_it_gains_variants(self):
        product = self._product("Becomes variant")
        self.env["website"]._recompute_stock_availability(product)
        self.assertTrue(self._rows(product))
        self._add_variants(product)
        self.env["website"]._recompute_stock_availability(product)
        self.assertTrue(self._rows(product), "new variants without stock do not make it reappear")
        self.assertNotIn(product.id, self._shop_ids(self.website))

    def test_drain_cron_roundtrip(self):
        product = self._product("Roundtrip")
        self.env["product.template.stock.dirty"].search([]).unlink()
        product._enqueue_stock_availability()
        self.env["website"]._cron_drain_stock_availability()
        self.assertTrue(self._rows(product))
        self.assertFalse(self.env["product.template.stock.dirty"].search([]))
        # restock -> hook enqueues -> drain removes the row
        self._set_stock(product, 4)
        self.env["website"]._cron_drain_stock_availability()
        self.assertFalse(self._rows(product))
        self.assertIn(product.id, self._shop_ids(self.website))

    def test_drain_clears_duplicate_rows_in_one_pass(self):
        # Repeated stock moves queue one row each; the drain must recompute the
        # product once and clear all of its rows, not one row per run.
        product = self._product("Queued many times")
        other = self._product("Queued once")
        Dirty = self.env["product.template.stock.dirty"]
        Dirty.search([]).unlink()
        for _ in range(4):
            product._enqueue_stock_availability()
        other._enqueue_stock_availability()
        self.assertEqual(Dirty.search_count([]), 5)
        self.env["website"]._cron_drain_stock_availability(batch=2)
        self.assertFalse(Dirty.search([]), "a single run must drain the whole queue")
        self.assertTrue(self._rows(product))
        self.assertTrue(self._rows(other))

    def test_settings_change_does_not_queue_every_candidate(self):
        # Saving the website settings must not enqueue one row per candidate:
        # reconciling the catalogue is the sweep's job, out of the request.
        self._product("Candidate A")
        self._product("Candidate B")
        Dirty = self.env["product.template.stock.dirty"]
        Dirty.search([]).unlink()
        self.website.out_of_stock_display = "show"
        self.website.out_of_stock_display = "hide"
        self.assertFalse(Dirty.search([]), "changing the setting must not flood the queue")

    def test_full_sweep_walks_every_candidate_and_resets_its_cursor(self):
        # batch=1 forces several passes: the sweep must resume from its cursor
        # and clear it once the catalogue is fully reconciled.
        product = self._product("Swept")
        Param = self.env["ir.config_parameter"].sudo()
        Param.set_int("website_sale_stock_hide_unavailable.sweep_cursor", 0)
        self.env["website"]._cron_full_sweep_stock_availability(batch=1)
        self.assertTrue(self._rows(product), "the sweep must reconcile every candidate")
        self.assertEqual(
            Param.get_int("website_sale_stock_hide_unavailable.sweep_cursor", 0),
            0,
            "a complete pass must reset the cursor",
        )

    def test_creating_website_in_hide_triggers_the_sweep(self):
        # A website born in hide/last has no precomputed data yet, so it must
        # ask the sweep to reconcile instead of waiting for the nightly run.
        sweep = self.env.ref("website_sale_stock_hide_unavailable.cron_full_sweep_stock_availability")
        Trigger = self.env["ir.cron.trigger"]
        before = Trigger.search_count([("cron_id", "=", sweep.id)])
        self.env["website"].create(
            {
                "name": "Shop born hidden",
                "company_id": self.company.id,
                "out_of_stock_display": "hide",
            }
        )
        self.assertGreater(
            Trigger.search_count([("cron_id", "=", sweep.id)]),
            before,
            "creating a website in hide must trigger the sweep",
        )

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
        self._set_stock(keep, 2)
        self.env["website"]._recompute_stock_availability(out + keep)
        unavailable = self.website._get_unavailable_tmpl_ids(out + keep)
        self.assertEqual(unavailable, {out.id})
        ordered = (out + keep).sorted(key=lambda p: p.id in unavailable)
        self.assertEqual(ordered[-1], out, "out-of-stock product goes last")

    def test_carousels_from_a_filter_hide_out_of_stock(self):
        in_stock = self._product("Carousel in stock")
        self._set_stock(in_stock, 5)
        sold_out = self._product("Carousel sold out")
        self.env["website"]._recompute_stock_availability(in_stock + sold_out)
        self.assertTrue(self._rows(sold_out))
        snippet = self._snippet_filter().with_context(website_id=self.website.id)
        # Return the records instead of rendering them: the override changes the
        # domain the snippet searches with, and rendering needs a bound request
        # and a fully configured shop.
        self.patch(type(snippet), "_filter_records_to_values", lambda self, records, **options: records)
        shown = snippet._prepare_values().product_tmpl_id
        self.assertIn(in_stock, shown)
        self.assertNotIn(sold_out, shown, "the carousels must not show what the shop hides")

    def _enable_native_unpublishing(self):
        feature = "website_sale.group_unpublish_out_of_stock"
        self.env.ref("website.group_website_restricted_editor")._apply_group(self.env.ref(feature))
        self.assertTrue(self.env["res.groups"]._is_feature_enabled(feature))

    def test_saving_the_settings_stores_the_choice_and_leaves_the_native_alone(self):
        # The real path, through res.config.settings: the module takes the group
        # off when it takes over and does not keep fighting for it afterwards.
        # Odoo reads the group before saving and writes back what it read, so a
        # module undoing it mid-save gets undone in turn -- and would break the
        # native feature for whoever does turn it back on.
        Groups = self.env["res.groups"]
        feature = "website_sale.group_unpublish_out_of_stock"
        self.assertFalse(Groups._is_feature_enabled(feature), "the install took it off")
        settings = self.env["res.config.settings"].create(
            {"website_id": self.website.id, "out_of_stock_display": "last"}
        )
        settings.execute()
        self.assertEqual(self.website.out_of_stock_display, "last")
        self.assertFalse(Groups._is_feature_enabled(feature))

    def test_install_republishes_what_the_native_had_unpublished(self):
        # Once the group is gone the native compute stops running, so what it
        # had taken down would stay down for good.
        Groups = self.env["res.groups"]
        feature = "website_sale.group_unpublish_out_of_stock"
        self._enable_native_unpublishing()
        product = self._product("Unpublished by Odoo")
        self.assertFalse(product.is_published, "the native one takes it down for having no stock")

        self.env["website"]._hide_unavailable_take_over_native()

        self.assertFalse(Groups._is_feature_enabled(feature))
        self.assertTrue(product.is_published, "its page must keep answering 200")

    def test_the_take_over_keeps_the_publish_date(self):
        # publish_date is a stored compute of is_published: letting it move
        # would send the whole backlog to the top of "Newest Arrivals".
        self._enable_native_unpublishing()
        product = self._product("Old arrival")
        was = fields.Datetime.to_datetime("2020-01-01 00:00:00")
        self.env.cr.execute("UPDATE product_template SET publish_date = %s WHERE id = %s", (was, product.id))
        product.invalidate_recordset(["publish_date"])

        self.env["website"]._hide_unavailable_take_over_native()

        self.assertTrue(product.is_published)
        self.assertEqual(product.publish_date, was)

    def test_the_take_over_leaves_the_rest_unpublished(self):
        self._enable_native_unpublishing()
        by_hand = self._product("Unpublished by hand")
        self._set_stock(by_hand, 5)
        self.assertTrue(by_hand.is_published, "with stock the native one leaves it published")
        by_hand.is_published = False
        self.env["website"]._hide_unavailable_take_over_native()
        self.assertFalse(by_hand.is_published, "with stock, the native one had not touched it")

    def test_nothing_is_queued_when_no_website_hides(self):
        # The module ships with the shop: a database where nobody turned it on
        # must not pay for it.
        self.website.out_of_stock_display = "show"
        product = self._product("Nobody uses it")
        self.env["product.template.stock.dirty"].search([]).unlink()
        self._set_stock(product, 5)
        self.assertFalse(
            self.env["product.template.stock.dirty"].search([]),
            "with no website hiding or pushing down, there is nothing to recompute",
        )

    def test_carousels_from_a_server_action_hide_out_of_stock(self):
        # The "Recently sold", "Recently viewed" and "Sold with" carousels are
        # backed by a server action, where filter_id is empty.
        in_stock = self._product("Action in stock")
        self._set_stock(in_stock, 5)
        sold_out = self._product("Action sold out")
        self.env["website"]._recompute_stock_availability(in_stock + sold_out)
        self.assertTrue(self._rows(sold_out))
        snippet = self._snippet_filter_server_action().with_context(website_id=self.website.id)
        shown = snippet._prepare_values().product_tmpl_id
        self.assertIn(in_stock, shown)
        self.assertNotIn(sold_out, shown, "a server-action carousel must not show what the shop hides")

    def test_archiving_a_variant_enqueues_the_template(self):
        # Availability is read over every variant, so archiving the only one
        # with stock changes what the shop shows.
        product = self._product("Variant archived")
        self._add_variants(product)
        self._set_variant_stock(product.product_variant_ids[0], 5)
        self.env["website"]._recompute_stock_availability(product)
        self.assertFalse(self._rows(product))
        self.env["product.template.stock.dirty"].search([]).unlink()
        product.product_variant_ids[0].action_archive()
        queued = self.env["product.template.stock.dirty"].search([]).product_tmpl_id
        self.assertIn(product, queued)

    def _confirmed_order(self, template, qty):
        partner = self.env["res.partner"].create({"name": "QA customer"})
        order = self.env["sale.order"].create(
            {
                "partner_id": partner.id,
                "order_line": [(0, 0, {"product_id": template.product_variant_id.id, "product_uom_qty": qty})],
            }
        )
        order.action_confirm()
        return order

    def _queued(self):
        return self.env["product.template.stock.dirty"].search([]).product_tmpl_id

    def test_changing_a_confirmed_order_line_enqueues(self):
        # The product has no stock, so with Inventory there is nothing to
        # reserve and no quant is written: the enqueue can only be this hook.
        # That is what makes this run in both worlds.
        product = self._product("Live order")
        order = self._confirmed_order(product, 1)
        self.env["product.template.stock.dirty"].search([]).unlink()
        order.order_line.product_uom_qty = 5
        self.assertIn(product, self._queued())

    def test_a_new_line_on_a_confirmed_order_enqueues(self):
        product = self._product("Grown order")
        other = self._product("Second product")
        order = self._confirmed_order(product, 1)
        self.env["product.template.stock.dirty"].search([]).unlink()
        self.env["sale.order.line"].create(
            {"order_id": order.id, "product_id": other.product_variant_id.id, "product_uom_qty": 1}
        )
        self.assertIn(other, self._queued())

    def test_a_line_on_a_draft_order_does_not_enqueue(self):
        # A quotation moves nothing: free_qty only counts confirmed lines.
        product = self._product("Quoted")
        partner = self.env["res.partner"].create({"name": "QA customer"})
        self.env["product.template.stock.dirty"].search([]).unlink()
        self.env["sale.order"].create(
            {
                "partner_id": partner.id,
                "order_line": [(0, 0, {"product_id": product.product_variant_id.id, "product_uom_qty": 1})],
            }
        )
        self.assertNotIn(product, self._queued())

    def test_a_confirmed_order_line_takes_the_product_out_of_the_shop(self):
        """Without Inventory, the confirmed line carries the outgoing quantity."""
        if "stock.quant" in self.env:
            self.skipTest("with Inventory the quant holds the reservation, not the line")
        product = self._product("Live order effect")
        self._set_stock(product, 10)
        order = self._confirmed_order(product, 1)
        self.env["website"]._cron_drain_stock_availability()
        self.assertFalse(self._rows(product), "free to sell, visible")

        order.order_line.product_uom_qty = 10
        self.env["website"]._cron_drain_stock_availability()
        self.assertTrue(self._rows(product), "nothing free to sell, hidden")

    def test_zeroing_a_confirmed_order_line_brings_the_product_back(self):
        # Odoo does not let a confirmed line be deleted; it asks for quantity 0.
        if "stock.quant" in self.env:
            self.skipTest("with Inventory the quant holds the reservation, not the line")
        product = self._product("Trimmed order")
        self._set_stock(product, 10)
        order = self._confirmed_order(product, 10)
        self.env["website"]._cron_drain_stock_availability()
        self.assertTrue(self._rows(product))

        order.order_line.product_uom_qty = 0
        self.env["website"]._cron_drain_stock_availability()
        self.assertFalse(self._rows(product), "with nothing ordered, the balance is back")

    def test_vendor_bill_brings_the_product_back(self):
        """Sin Inventario, el stock entra por la factura de proveedor."""
        if "stock.quant" in self.env:
            self.skipTest("con Inventario el stock sale de los quants, no de la factura")
        product = self._product("Repuesto")
        self.env["website"]._recompute_stock_availability(product)
        self.assertTrue(self._rows(product), "sin stock, oculto")
        self.assertNotIn(product.id, self._shop_ids(self.website))

        partner = self.env["res.partner"].create({"name": "Proveedor QA"})
        bill = self.env["account.move"].create(
            {
                "move_type": "in_invoice",
                "partner_id": partner.id,
                "invoice_date": fields.Date.today(),
                "invoice_line_ids": [
                    (0, 0, {"product_id": product.product_variant_id.id, "quantity": 5, "price_unit": 10.0})
                ],
            }
        )
        bill.action_post()
        self.env.invalidate_all()

        queued = self.env["product.template.stock.dirty"].search([]).product_tmpl_id
        self.assertIn(product, queued, "publicar la factura tiene que encolar el producto")
        self.env["website"]._recompute_stock_availability(product)
        self.assertFalse(self._rows(product), "con stock de la factura, vuelve a verse")
        self.assertIn(product.id, self._shop_ids(self.website))
