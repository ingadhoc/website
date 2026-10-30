from odoo import api, models

# Columns of a confirmed line that move the outgoing quantity free_qty
# subtracts (sale.product.product._compute_forecasted_without_stock).
# qty_invoiced is left out on purpose: it is a stored compute with no inverse,
# flushed straight to the column, so it never reaches write(). Invoicing is
# covered by the qty_available write it makes on the variant.
RECOMPUTE_TRIGGER_FIELDS = {"product_id", "product_uom_qty", "product_uom_id"}


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.model_create_multi
    def create(self, vals_list):
        lines = super().create(vals_list)
        lines._enqueue_hide_unavailable()
        return lines

    def write(self, vals):
        res = super().write(vals)
        if RECOMPUTE_TRIGGER_FIELDS & vals.keys():
            self._enqueue_hide_unavailable()
        return res

    def _enqueue_hide_unavailable(self):
        confirmed = self.filtered(lambda line: line.order_id.state == "sale")
        confirmed.product_id.product_tmpl_id._hide_unavailable_enqueue_candidates()
