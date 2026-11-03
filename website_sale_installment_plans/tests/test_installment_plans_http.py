from odoo.tests import HttpCase, tagged
from odoo.tools import format_amount


@tagged("post_install", "-at_install")
class TestInstallmentPlansHttp(HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.website = cls.env.ref("base.default_website")
        Installment = cls.env["account.card.installment"]
        Installment.search([]).is_published = False
        card = cls.env["account.card"].create({"name": "Card", "company_id": cls.website.company_id.id})
        Installment.create(
            {
                "card_id": card.id,
                "name": "3",
                "divisor": 3,
                "installment": 3,
                "surcharge_coefficient": 1.2,
                "is_published": True,
            }
        )
        cls.templates = cls.env["product.template"].create(
            [
                {"name": f"Installment product {i}", "list_price": 300.0, "is_published": True, "sale_ok": True}
                for i in range(3)
            ]
        )

    def test_combination_info_route(self):
        product = self.templates[0].product_variant_id
        res = self.make_jsonrpc_request(
            "/website_sale/get_combination_info",
            params={
                "product_template_id": self.templates[0].id,
                "product_id": product.id,
                "combination": product.product_template_attribute_value_ids.ids,
                "add_qty": 1.0,
            },
        )
        # The route answers in the website language.
        env = self.env(context={"lang": self.website.default_lang_id.code})
        currency = self.website.currency_id
        self.assertIn(format_amount(env, 120.0, currency), res["installment_plans"])
        self.assertIn(format_amount(env, 360.0, currency), res["installment_plans"])

    def test_plans_searched_once_per_request(self):
        Installment = self.registry["account.card.installment"]
        search = Installment.search
        calls = []

        def counted_search(model, domain, *args, **kwargs):
            if ("is_published", "=", True) in domain:
                calls.append(domain)
            return search(model, domain, *args, **kwargs)

        self.patch(Installment, "search", counted_search)
        res = self.url_open("/shop?search=Installment product")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.text.count("installment-plans"), 3)
        self.assertEqual(len(calls), 1)
