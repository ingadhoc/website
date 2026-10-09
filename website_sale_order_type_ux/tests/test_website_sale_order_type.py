##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo.addons.website_sale.tests.common import MockRequest, WebsiteSaleCommon
from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestWebsiteSaleOrderType(WebsiteSaleCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.warehouse = cls.env["stock.warehouse"].create(
            {
                "name": "Website Type Warehouse",
                "code": "WTW",
                "company_id": cls.env.company.id,
            }
        )
        cls.website_type = cls.env["sale.order.type"].create(
            {
                "name": "Website Type",
                "warehouse_id": cls.warehouse.id,
            }
        )
        cls.partner_type = cls.env["sale.order.type"].create({"name": "Partner Type"})
        cls.website.sale_order_type_id = cls.website_type
        cls.partner.sale_type = False

    def _prepare_values(self, partner):
        with MockRequest(self.env, website=self.website):
            return self.website._prepare_sale_order_values(partner.sudo())

    def test_prepare_values_use_website_type_and_its_warehouse(self):
        values = self._prepare_values(self.partner)
        self.assertEqual(values.get("type_id"), self.website_type.id)
        self.assertEqual(values.get("warehouse_id"), self.warehouse.id)

    def test_prepare_values_prefer_partner_type(self):
        self.partner.sudo().sale_type = self.partner_type
        values = self._prepare_values(self.partner)
        self.assertEqual(values.get("type_id"), self.partner_type.id)
        self.assertNotIn("warehouse_id", values)

    def test_compute_uses_website_type_when_partner_has_none(self):
        order = self.env["sale.order"].create({"partner_id": self.partner.id, "website_id": self.website.id})
        self.assertEqual(order.type_id, self.website_type)

    def test_compute_prefers_partner_type(self):
        self.partner.sudo().sale_type = self.partner_type
        order = self.env["sale.order"].create({"partner_id": self.partner.id, "website_id": self.website.id})
        self.assertEqual(order.type_id, self.partner_type)

    def test_compute_falls_back_without_website_type(self):
        self.website.sudo().sale_order_type_id = False
        order = self.env["sale.order"].create({"partner_id": self.partner.id, "website_id": self.website.id})
        self.assertEqual(order.type_id, self.env.ref("sale_order_type.normal_sale_type"))
        self.assertNotEqual(order.type_id, self.website_type)

    def test_commercial_partner_type_differs_between_cart_and_backend(self):
        # Characterizes current behavior, not a decision: for a contact without
        # type whose company has one, the cart only looks at the contact and
        # takes the website type, while the compute also looks at the
        # commercial partner. Whether this is a bug is still open.
        partners = self.env["res.partner"].sudo()
        company = partners.create({"name": "Typed Company", "is_company": True})
        company.sale_type = self.partner_type
        contact = partners.create({"name": "Contact", "parent_id": company.id})
        contact.sale_type = False
        values = self._prepare_values(contact)
        self.assertEqual(values.get("type_id"), self.website_type.id)
        order = self.env["sale.order"].create({"partner_id": contact.id, "website_id": self.website.id})
        self.assertEqual(order.type_id, self.partner_type)
