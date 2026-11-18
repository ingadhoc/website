from odoo.tests import HttpCase, tagged


@tagged("post_install", "-at_install")
class TestWebsiteSaleSearchImproved(HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        tag = cls.env["product.tag"].create({"name": "Test Tag", "visible_on_ecommerce": True})
        cls.env["product.template"].create(
            {
                "name": "Test Product",
                "type": "consu",
                "description_ecommerce": "Test Description",
                "is_published": True,
                "product_tag_ids": [(4, tag.id)],
            }
        )

    def test_website_sale_search_improved(self):
        self.env["ir.config_parameter"].create(
            {
                "key": "website_sale_search_improved.search_fields",
                "value": "['description_ecommerce','product_tag_ids.name']",
            }
        )

        self.env["ir.config_parameter"].create(
            {"key": "website_sale_search_improved.extend_search_fields", "value": "True"}
        )

        self.start_tour(
            "/shop",
            "website_sale_search_improved_tour",
            login="admin",
        )

    def _search_with_fuzzy(self, search):
        website = self.env.ref("website.default_website")
        options = {
            "displayDescription": True,
            "displayDetail": True,
            "displayImage": True,
            "displayExtraLink": True,
            "display_currency": website.currency_id,
            "allowFuzzy": True,
        }
        return website.with_context(website_id=website.id)._search_with_fuzzy(
            "products_only", search, 5, "name asc", options
        )

    def test_exact_search_keeps_non_stored_fields(self):
        # barcode is not stored, so the fuzzy search drops it; the exact search must still use it
        product = self.env["product.template"].create(
            {"name": "Striped Product", "type": "consu", "barcode": "7790048151", "is_published": True}
        )
        self.env["ir.config_parameter"].set_param("website_sale_search_improved.search_fields", "['barcode']")
        self.env["ir.config_parameter"].set_param("website_sale_search_improved.extend_search_fields", "True")
        self.env.flush_all()
        for search in ("7790048151", "Striped 7790048151"):
            _count, results, _fuzzy_term = self._search_with_fuzzy(search)
            self.assertIn(product, results[0]["results"], search)

    def test_fuzzy_term_keeps_many2one_in_exact_search(self):
        category = self.env["product.category"].create({"name": "Zebracat"})
        self.env["product.template"].create(
            {"name": "Striped Product", "type": "consu", "categ_id": category.id, "is_published": True}
        )
        self.env["product.template"].create({"name": "Zebracat", "type": "consu", "is_published": True})
        self.env["ir.config_parameter"].set_param("website_sale_search_improved.search_fields", "['categ_id.name']")
        self.env["ir.config_parameter"].set_param("website_sale_search_improved.extend_search_fields", "True")
        self.env.flush_all()
        # The fuzzy search fixes the term using the product name; the exact search must still use the many2one path
        count, _results, fuzzy_term = self._search_with_fuzzy("Zebrakat")
        self.assertEqual(fuzzy_term.lower(), "zebracat")
        self.assertEqual(count, 2)
