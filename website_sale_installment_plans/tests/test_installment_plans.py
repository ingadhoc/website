from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestInstallmentPlans(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.website = cls.env["website"].create({"name": "Installments", "company_id": cls.env.company.id})
        cls.env = cls.env(context=dict(cls.env.context, website_id=cls.website.id))
        Installment = cls.env["account.card.installment"]
        # Plans of other tests or demo data must not interfere.
        Installment.search([]).is_published = False
        cls.card = cls.env["account.card"].create({"name": "Card", "company_id": cls.env.company.id})
        cls.plan_three = Installment.create(
            {
                "card_id": cls.card.id,
                "name": "3",
                "divisor": 3,
                "installment": 3,
                "surcharge_coefficient": 1.2,
                "message": "with surcharge",
                "is_published": True,
            }
        )
        cls.plan_one = Installment.create(
            {
                "card_id": cls.card.id,
                "name": "1",
                "divisor": 1,
                "installment": 1,
                "surcharge_coefficient": 1.0,
                "is_published": True,
            }
        )
        cls.template = cls.env["product.template"].create({"name": "Product", "list_price": 300.0})

    def test_plans_values(self):
        """Plans come ordered by divisor, with the same numbers the legend showed in 19.0."""
        self.assertEqual(
            self.template._get_installment_plans(300.0),
            [
                {"count": 1, "amount": 300.0, "total": 300.0, "message": ""},
                {"count": 3, "amount": 120.0, "total": 360.0, "message": "with surcharge"},
            ],
        )

    def test_no_plans_without_price(self):
        self.assertEqual(self.template._get_installment_plans(0.0), [])

    def test_only_published_plans_of_active_cards_of_the_company(self):
        other_company = self.env["res.company"].create({"name": "Other"})
        other_card = self.env["account.card"].create({"name": "Other", "company_id": other_company.id})
        archived_card = self.env["account.card"].create({"name": "Archived", "company_id": self.env.company.id})
        shared_card = self.env["account.card"].create({"name": "Shared", "company_id": False})
        Installment = self.env["account.card.installment"]
        for card in other_card | archived_card | shared_card:
            Installment.create(
                {"card_id": card.id, "name": card.name, "divisor": 6, "installment": 6, "is_published": True}
            )
        Installment.create({"card_id": self.card.id, "name": "Hidden", "divisor": 12, "installment": 12})
        archived_card.action_archive()

        self.assertEqual(
            self.template._get_published_installments(),
            self.plan_one | self.plan_three | shared_card.installment_ids,
        )

    def test_legend_rendering(self):
        """The legend uses the currency format of the website and the theme classes."""
        html = str(
            self.env["ir.qweb"]._render(
                "website_sale_installment_plans.installment_plans",
                {
                    "installment_plans": self.template._get_installment_plans(1234.5),
                    "website": self.website,
                },
            )
        )
        self.assertIn("oe_currency_value", html)
        self.assertIn("with surcharge", html)
        self.assertNotIn("style=", html)
        self.assertEqual(
            str(
                self.env["ir.qweb"]._render(
                    "website_sale_installment_plans.installment_plans",
                    {"installment_plans": [], "website": self.website},
                )
            ).strip(),
            "",
        )
