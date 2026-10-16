from odoo.exceptions import UserError
from odoo.tests import HttpCase, tagged


@tagged("post_install", "-at_install")
class TestWebsiteSaleSearchImproved(HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # website_meta_keywords is not searched natively by website_sale, so only the
        # module makes the product show up when searching by it
        cls.product = cls.env["product.template"].create(
            {
                "name": "Test Product",
                "type": "consu",
                "list_price": 100.0,
                "website_meta_keywords": "Test Keyword",
                "is_published": True,
            }
        )
        cls.website = cls.env.ref("base.default_website")

    def _enable_extra_search_fields(self):
        self.env["ir.config_parameter"].set_bool("website_sale_search_improved.extend_search_fields", True)
        self.env["ir.config_parameter"].set_str(
            "website_sale_search_improved.search_fields",
            "['website_meta_keywords']",
        )

    def _search_products(self, term):
        options = {
            "displayDescription": True,
            "displayDetail": True,
            "displayImage": True,
            "displayExtraLink": True,
            "display_currency": self.website.currency_id,
            "allowFuzzy": True,
        }
        website = self.website.with_context(website_id=self.website.id)
        _count, details, _fuzzy = website._search_with_fuzzy("product_template", term, 0, 20, "name asc", options)
        return details[0]["results"] if details else self.env["product.template"]

    def test_search_extra_field(self):
        self.env["ir.config_parameter"].set_bool("website_sale_search_improved.extend_search_fields", False)
        self.assertNotIn(self.product, self._search_products("Test Keyword"))
        self._enable_extra_search_fields()
        self.assertIn(self.product, self._search_products("Test Keyword"))

    def test_website_sale_search_improved(self):
        self._enable_extra_search_fields()
        self.start_tour(
            "/shop",
            "website_sale_search_improved_tour",
            login="admin",
        )

    def test_search_fields_reject_many2one(self):
        with self.assertRaises(UserError):
            self.env["res.config.settings"].create({"website_search_fields_list": "['categ_id.name']"})

    def test_fuzzy_term_keeps_many2one_in_exact_search(self):
        # Databases saved before the settings validation may still have many2one paths
        category = self.env["product.category"].create({"name": "Zebracat"})
        self.env["product.template"].create(
            {"name": "Striped Product", "type": "consu", "categ_id": category.id, "is_published": True}
        )
        self.env["product.template"].create({"name": "Zebracat", "type": "consu", "is_published": True})
        self.env["ir.config_parameter"].set_str("website_sale_search_improved.search_fields", "['categ_id.name']")
        self.env["ir.config_parameter"].set_bool("website_sale_search_improved.extend_search_fields", True)
        self.env.flush_all()
        options = {
            "displayDescription": True,
            "displayDetail": True,
            "displayImage": True,
            "displayExtraLink": True,
            "display_currency": self.website.currency_id,
            "allowFuzzy": True,
        }
        website = self.website.with_context(website_id=self.website.id)
        # The fuzzy search fixes the term using the product name; the exact search must still use the many2one path
        count, _results, fuzzy_term = website._search_with_fuzzy(
            "product_template", "Zebrakat", 0, 5, "name asc", options
        )
        self.assertEqual(fuzzy_term.lower(), "zebracat")
        self.assertEqual(count, 2)
