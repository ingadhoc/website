from odoo import fields, models


class Website(models.Model):
    _inherit = "website"

    ga4_api_secret = fields.Char(
        string="GA4 API Secret",
        groups="base.group_system",
        help=(
            "Measurement Protocol API Secret generated in GA4 admin.\n"
            "Required to send server-side events (purchase, refund).\n"
            "Generate one at: Admin → Data Streams → your stream → Measurement Protocol API secrets."
        ),
    )

    def _retry_failed_ga4_mp_events(self):
        """Cron: retry Measurement Protocol payloads that failed on the first attempt.

        Called once (not per website) so each pending record is processed
        exactly once regardless of the number of websites.
        """
        max_attempts = 5

        orders = self.env["sale.order"].sudo().search([("ga4_mp_pending_payload", "!=", False)])
        for order in orders:
            payload = order.ga4_mp_pending_payload or {}
            attempts = payload.get("_attempts", 0)
            if attempts >= max_attempts:
                order.ga4_mp_pending_payload = False
                continue
            sent = order._send_ga4_mp_event(
                payload.get("event_name", ""),
                payload.get("params", {}),
                _is_retry=True,
            )
            if sent:
                order.ga4_mp_pending_payload = False

        moves = self.env["account.move"].sudo().search([("ga4_mp_pending_payload", "!=", False)])
        for move in moves:
            payload = move.ga4_mp_pending_payload or {}
            attempts = payload.get("_attempts", 0)
            if attempts >= max_attempts:
                move.ga4_mp_pending_payload = False
                continue
            sent = move._send_ga4_mp_refund(_is_retry=True)
            if sent:
                move.ga4_mp_pending_payload = False
