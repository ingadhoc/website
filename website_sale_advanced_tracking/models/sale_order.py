from odoo import models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def prepare_purchase_information(self):
        products = []
        for line in self.order_line:
            products.append(
                {
                    "item_id": line.product_id.default_code or line.product_id.id,
                    "item_name": line.product_id.name,
                    "item_category": line.product_id.categ_id.name,
                    "quantity": line.product_uom_qty,
                    "price": line.price_reduce_taxinc,
                }
            )
        res = {
                'transaction_id': self.id,
                'value': self.amount_total,
                'tax': self.amount_tax,
                'currency': self.currency_id.name,
                'items': products
            }
        return res
