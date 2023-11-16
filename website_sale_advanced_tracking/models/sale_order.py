from odoo import models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def prepare_purchase_information(self):
        products = []
        for line in self.order_line:
            products.append(
                {
                    "id": line.product_id.default_code or line.product_id.id,
                    "name": line.product_id.name,
                    "category": line.product_id.categ_id.name,
                    "quantity": line.product_uom_qty,
                    "price": line.price_subtotal,
                }
            )
        res = {
            'purchase': {
                    'actionField': {
                        'id': self.id,
                        'affiliation': self.partner_id.name,
                        'revenue': self.amount_total,
                        'tax':self.amount_tax,
                    },
                    'products': products
            }
        }
        return res
