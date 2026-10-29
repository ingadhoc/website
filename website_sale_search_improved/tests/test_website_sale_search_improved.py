from odoo.exceptions import UserError
from odoo.tests import HttpCase, tagged


@tagged("post_install", "-at_install")
class TestWebsiteSaleSearchImproved(HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        tag = cls.env["product.tag"].create({"name": "Test Tag", "visible_to_customers": True})
        cls.env["product.template"].create(
            {
                "name": "Test Product",
                "type": "consu",
                "list_price": 100.0,
                "description_ecommerce": "Test Description",
                "is_published": True,
                "product_tag_ids": [(4, tag.id)],
            }
        )

    def test_website_sale_search_improved(self):
        self.env["ir.config_parameter"].set_param(
            "website_sale_search_improved.search_fields",
            "['description_ecommerce','product_tag_ids.name']",
        )

        self.env["ir.config_parameter"].set_param("website_sale_search_improved.extend_search_fields", "True")

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
        self.env["ir.config_parameter"].set_param("website_sale_search_improved.search_fields", "['categ_id.name']")
        self.env["ir.config_parameter"].set_param("website_sale_search_improved.extend_search_fields", "True")
        self.env.flush_all()
        website = self.env.ref("website.default_website")
        options = {
            "displayDescription": True,
            "displayDetail": True,
            "display_currency": True,
            "displayExtraDetail": True,
            "displayExtraLink": True,
            "displayImage": True,
            "allowFuzzy": True,
        }
        # The fuzzy search fixes the term using the product name; the exact search must still use the many2one path
        count, _results, fuzzy_term = website._search_with_fuzzy("products_only", "Zebrakat", 5, "name asc", options)
        self.assertEqual(fuzzy_term.lower(), "zebracat")
        self.assertEqual(count, 2)
