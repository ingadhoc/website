from odoo import models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def prepare_checkout_information(self):
        """Return a GA4-compatible items list for this set of order lines.

        Used by QWeb templates to embed cart data as JSON and by
        prepare_purchase_information() on sale.order.
        """
        result = []
        for line in self.filtered(lambda l: not l.is_delivery):
            result.append(
                {
                    "item_id": line.product_id.barcode or str(line.product_id.id),
                    "item_name": line.product_id.name or "-",
                    "item_category": line.product_id.categ_id.name or "-",
                    "currency": line.currency_id.name,
                    "price": line.price_reduce_taxinc,
                    "quantity": line.product_uom_qty,
                }
            )
        return result
