import time

from odoo import fields, models

# Meta rejects a whole request if any event is older than 7 days.
FACEBOOK_CAPI_MAX_EVENT_AGE_DAYS = 7


class Website(models.Model):
    _inherit = "website"

    facebook_pixel_key = fields.Char("Facebook pixel ID")
    facebook_capi_access_token = fields.Char(
        string="Facebook CAPI Access Token",
        groups="base.group_system",
        help=(
            "Conversions API access token used to send server-side events.\n"
            "Generate one at: Events Manager → your Pixel → Settings → "
            "Conversions API → Generate access token.\n"
            "The Pixel ID above is reused as the dataset ID of the endpoint."
        ),
    )

    def _retry_failed_facebook_capi_events(self):
        """Cron: retry Conversions API payloads that failed on the first attempt.

        Called once (not per website) so each pending record is processed
        exactly once regardless of the number of websites. Payloads whose
        ``event_time`` is older than 7 days are discarded (Meta hard limit).
        """
        max_attempts = 5
        max_age_seconds = FACEBOOK_CAPI_MAX_EVENT_AGE_DAYS * 24 * 3600
        now = int(time.time())

        # Cap per run: each pending order does a blocking HTTP call, so a large
        # backlog (e.g. after a Meta outage) drains across successive runs
        # instead of one run running for hours and overlapping the next.
        orders = self.env["sale.order"].sudo().search([("facebook_capi_pending_payload", "!=", False)], limit=200)
        for order in orders:
            payload = order.facebook_capi_pending_payload or {}
            attempts = payload.get("_attempts", 0)
            event_time = payload.get("event_time", 0)
            too_old = event_time and (now - event_time) > max_age_seconds
            if attempts >= max_attempts or too_old:
                order.facebook_capi_pending_payload = False
                continue
            sent = order._send_facebook_capi_event(
                payload.get("event_name", ""),
                payload.get("custom_data", {}),
                _is_retry=True,
                event_time=event_time or None,
            )
            if sent:
                order.facebook_capi_pending_payload = False
