from odoo import models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def ga4_checkout_information(self):
        """Return a GA4-compatible items list for this set of order lines.

        Used by QWeb templates to embed cart data as JSON and by
        ga4_purchase_information() on sale.order.

        NOTE: intentionally GA4-namespaced. It must NOT reuse the
        ``prepare_checkout_information`` name owned by
        ``website_sale_advanced_tracking`` (which returns a JSON *string*):
        both modules can be installed side by side and overriding that method
        with a different return type (list) breaks the JSON.parse of the
        facebook_pixel / GTM checkout interactions (task 121712).
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
