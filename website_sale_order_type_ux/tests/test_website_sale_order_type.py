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
        self.assertEqual(values.get("company_id"), self.warehouse.company_id.id)

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
        self.assertEqual(order.type_id, self.env["sale.order"]._default_type_id())
