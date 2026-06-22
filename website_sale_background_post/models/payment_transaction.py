##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import api, fields, models


class PaymentTransaction(models.Model):
    _inherit = "payment.transaction"

    to_defer = fields.Boolean(
        string="Defer Invoice Posting",
        compute="_compute_to_defer",
        store=True,
        help="True when this transaction is linked to a website order whose company has "
        "background invoice posting enabled.",
    )

    @api.depends("state", "sale_order_ids")
    def _compute_to_defer(self):
        for tx in self:
            tx.to_defer = tx.state == "done" and any(
                so.website_id and so.company_id.website_sale_background_post for so in tx.sale_order_ids
            )

    def _post_process(self):
        deferred = self.filtered("to_defer")
        if not deferred:
            return super()._post_process()

        others = self - deferred
        if others:
            super(PaymentTransaction, others)._post_process()
        super(
            PaymentTransaction,
            deferred.with_context(website_force_background_post=True),
        )._post_process()
        self.env.ref("account_background_post.ir_cron_background_post_invoices")._trigger()
