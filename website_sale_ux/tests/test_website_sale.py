# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo.tests import HttpCase, tagged


@tagged('post_install', '-at_install')
class TestWebsiteSale(HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        company = cls.env.ref('l10n_ar.company_ri')
        company.write({'restrict_sales': False})
        cls.env.company = company
        cls.env.ref('base.user_admin').write({
            'company_id': company.id,
            'company_ids': [(6, 0, [company.id])],
        })
        tax = cls.env['account.tax'].search([('name', '=', 'IVA 21%'), ('type_tax_use', '=', 'sale')], limit=1)
        product = cls.env["product.template"].create(
            {
                "name": "Test Product",
                "type": "product",
                "list_price": 100,
                "is_published": True,
                "taxes_id": [(4, tax.id)]
            }
        )
        cls.env["stock.quant"].create(
            [
                {
                    "product_id": product.product_variant_id.id,
                    "location_id": cls.env.ref("stock.stock_location_stock").id,
                    "quantity": 30.0,
                },
            ]
        )
        cls.env.ref('delivery.product_product_delivery').write({'taxes_id': [(4, tax.id)]})
        cls.env.ref('l10n_ar_website_sale.default_website_ri').write({'sequence': 1})
        cls.env.ref('payment.payment_provider_transfer').write({'state': 'test', 'is_published': True, 'company_id': company.id})
        journal = cls.env['account.journal'].search([('name', '=', 'Banco'), ('company_id', '=', company.id)], limit=1)
        cls.env.ref('payment.payment_provider_demo').write({'state': 'test', 'is_published': True, 'company_id': company.id, 'journal_id': journal.id if journal else False})

    def test_website_sale_wire_transfer(self):
        self.start_tour(
            "/shop",
            'website_sale_tour_wire_transfer',
            login="admin",
        )
        sale_order_line = self.env['sale.order.line'].search([('product_id.name', '=', 'Test Product')], limit=1, order='id desc')
        self.assertTrue(sale_order_line, "No sale order line found for 'Test Product 1'")
        if sale_order_line:
            sale_order = sale_order_line.order_id
            # Queda en estado enviado porque espera el pago
            self.assertEqual(sale_order.state, 'sent', "Sale order is not in 'sent' state")

    def test_website_sale_demo(self):
        self.start_tour(
            "/shop",
            'website_sale_tour_demo',
            login="admin",
        )
        sale_order_line = self.env['sale.order.line'].search([('product_id.name', '=', 'Test Product')], limit=1, order='id desc')
        self.assertTrue(sale_order_line, "No sale order line found for 'Test Product'")
        if sale_order_line:
            sale_order = sale_order_line.order_id
            self.assertEqual(sale_order.state, 'sale', "Sale order is not in 'sale' state")
