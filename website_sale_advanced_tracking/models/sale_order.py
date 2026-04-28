import json

from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def prepare_purchase_information(self):
        products = []
        discount = 0.0
        shipping = 0.0
        for line in self.order_line:
            if getattr(line, "is_reward_line", False):
                discount += abs(line.price_reduce_taxinc * line.product_uom_qty)
            elif getattr(line, "is_delivery", False):
                shipping += line.price_reduce_taxinc * line.product_uom_qty
            else:
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
            "transaction_id": self.id,
            "value": self.amount_total,
            "tax": self.amount_tax,
            "shipping": shipping,
            "discount": discount,
            "currency": self.currency_id.name,
            "items": products,
        }
        return json.dumps(res)
