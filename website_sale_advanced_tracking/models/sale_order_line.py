import json

from odoo import models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def prepare_checkout_information(self):
        res = []
        for line in self:
            res.append(
                {
                    "item_name": line.product_id.name,
                    "item_id": line.product_id.default_code or line.product_id.id,
                    "price": line.price_reduce_taxinc,
                    "quantity": line.product_uom_qty,
                    "is_reward_line": getattr(line, "is_reward_line", False),
                }
            )
        return json.dumps(res)
