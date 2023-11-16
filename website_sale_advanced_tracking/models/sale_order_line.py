from odoo import models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def prepare_checkout_information(self):
        res = []
        for line in self:
            res.append(
                {
                    'item_name': line.name,
                    'item_id': line.product_id.default_code or line.product_id.id,
                    'price': (line.price_reduce_taxinc / line.product_uom_qty),
                    'quantity': line.product_uom_qty
                }
            )
        return res
