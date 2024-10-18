from odoo.tests import HttpCase, tagged


@tagged('post_install', '-at_install')
class TestWebsiteSaleSearchImproved(HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        tag = cls.env['product.tag'].create({
            "name": "Test Tag",
            "visible_on_ecommerce": True
        })
        cls.env["product.template"].create({
            "name": "Test Product",
            "type": "consu",
            "description_ecommerce": "Test Description",
            "is_published": True,
            "product_tag_ids": [(4, tag.id)]
        })

    def test_website_sale_search_improved(self):
        self.env['ir.config_parameter'].create({
           'key': "website_sale_search_improved.search_fields",
           'value': "['description_ecommerce','product_tag_ids.name']"
        })

        self.env['ir.config_parameter'].create({
           'key': "website_sale_search_improved.extend_search_fields",
           'value': "True"
        })

        self.start_tour(
            "/shop",
            'website_sale_search_improved_tour',
            login="admin",
        )
