from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_confirm(self):
        # A confirmed order is outgoing quantity, which free_qty subtracts
        # (sale.product.product._compute_forecasted_without_stock).
        res = super().action_confirm()
        self._enqueue_hide_unavailable()
        return res

    def _action_cancel(self):
        res = super()._action_cancel()
        self._enqueue_hide_unavailable()
        return res

    def _enqueue_hide_unavailable(self):
        self.order_line.product_id.product_tmpl_id._hide_unavailable_enqueue_candidates()
