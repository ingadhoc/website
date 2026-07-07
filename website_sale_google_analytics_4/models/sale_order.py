import logging

import requests
from odoo import api, fields, models

_logger = logging.getLogger(__name__)

GA4_MP_ENDPOINT = "https://www.google-analytics.com/mp/collect"
GA4_MP_TIMEOUT = 3  # seconds – must not block payment flow


class SaleOrder(models.Model):
    _inherit = "sale.order"

    ga_client_id = fields.Char(
        string="GA Client ID",
        help="Parsed from the _ga browser cookie at checkout start.",
        copy=False,
    )
    ga_session_id = fields.Char(
        string="GA Session ID",
        help="Parsed from the _ga_<container> browser cookie at checkout start.",
        copy=False,
    )
    ga4_mp_pending_payload = fields.Json(
        string="GA4 MP Pending Payload",
        help="Stores a failed Measurement Protocol payload for retry by the scheduled action.",
        copy=False,
    )

    # ------------------------------------------------------------------
    # Public helpers used by templates
    # ------------------------------------------------------------------

    def ga4_purchase_information(self):
        """Return a GA4-compatible purchase dict for this order.

        ``transaction_id`` is ``self.id`` (integer) to match the value
        emitted by the native website_sale Tracking interaction so that
        GA4 can deduplicate the frontend and backend ``purchase`` events.

        Returns an empty dict when called on an empty recordset so that
        QWeb templates can call this method safely in all contexts.

        NOTE: intentionally GA4-namespaced. It must NOT reuse the
        ``prepare_purchase_information`` name owned by
        ``website_sale_advanced_tracking`` (which returns a JSON *string*):
        both modules can be installed side by side and overriding that method
        with a different return type (dict) breaks the JSON.parse of the
        facebook_pixel / GTM checkout interactions (task 121712).
        """
        if not self:
            return {}
        self.ensure_one()
        delivery_line = self.order_line.filtered("is_delivery")
        # GA4 spec: value = sum(price × qty) for items, shipping and tax separate.
        # Use price_total (tax-inclusive) to stay consistent with the item prices
        # emitted by ga4_checkout_information() which uses price_reduce_taxinc.
        delivery_total = sum(delivery_line.mapped("price_total")) if delivery_line else 0.0
        info = {
            "transaction_id": str(self.id),
            "affiliation": self.company_id.name,
            "value": self.amount_total - delivery_total,
            "tax": self.amount_tax,
            "currency": self.currency_id.name,
            "items": self.order_line.ga4_checkout_information(),
        }
        if delivery_line:
            info["shipping"] = delivery_total
        return info

    # ------------------------------------------------------------------
    # Measurement Protocol
    # ------------------------------------------------------------------

    def _send_ga4_mp_event(self, event_name, params, _is_retry=False):
        """Send a single event to the GA4 Measurement Protocol.

        Returns True on success, False on failure.
        On failure the payload is persisted in ``ga4_mp_pending_payload``
        for later retry by the cron (unless this call IS the retry).
        """
        self.ensure_one()
        website = (self.website_id or self.env["website"].get_current_website()).sudo()
        measurement_id = website.google_analytics_key
        api_secret = website.ga4_api_secret

        if not measurement_id or not api_secret:
            return False
        if not self.ga_client_id:
            return False

        event_params = dict(params)
        # Required for session-scoped metrics
        if self.ga_session_id:
            event_params["session_id"] = self.ga_session_id
        event_params.setdefault("engagement_time_msec", 100)

        body = {
            "client_id": self.ga_client_id,
            "events": [{"name": event_name, "params": event_params}],
        }

        try:
            response = requests.post(
                GA4_MP_ENDPOINT,
                params={"measurement_id": measurement_id, "api_secret": api_secret},
                json=body,
                timeout=GA4_MP_TIMEOUT,
            )
            response.raise_for_status()
            _logger.info(
                "GA4 MP event '%s' sent for order %s",
                event_name,
                self.name,
            )
            return True
        except Exception as exc:
            _logger.warning(
                "GA4 MP event '%s' failed for order %s: %s",
                event_name,
                self.name,
                exc,
            )
            if not _is_retry:
                attempts = (self.ga4_mp_pending_payload or {}).get("_attempts", 0)
                self.ga4_mp_pending_payload = {
                    "event_name": event_name,
                    "params": params,
                    "_attempts": attempts + 1,
                }
            else:
                payload = dict(self.ga4_mp_pending_payload or {})
                payload["_attempts"] = payload.get("_attempts", 0) + 1
                self.ga4_mp_pending_payload = payload
            return False

    # ------------------------------------------------------------------
    # Confirmation hook – server-side purchase event
    # ------------------------------------------------------------------

    def _action_confirm(self):
        """Send a backend purchase event after confirmation.

        GA4 deduplicates with the frontend event via the same
        ``transaction_id`` (order.id).  The backend event is a
        reliability safeguard for ad-blocker and async-payment cases.
        """
        res = super()._action_confirm()
        for order in self:
            try:
                params = order.ga4_purchase_information()
                order._send_ga4_mp_event("purchase", params)
            except Exception as exc:
                _logger.warning(
                    "GA4 MP purchase event skipped for order %s: %s",
                    order.name,
                    exc,
                )
        return res

    # ------------------------------------------------------------------
    # Cookie parsing utilities (called from controller)
    # ------------------------------------------------------------------

    @api.model
    def _parse_ga_client_id(self, cookie_value):
        """Extract client_id from ``_ga`` cookie value.

        ``_ga`` format: ``GA1.1.<cid_part1>.<cid_part2>``
        client_id = ``<cid_part1>.<cid_part2>``
        """
        if not cookie_value:
            return ""
        parts = cookie_value.split(".")
        if len(parts) >= 4:
            return ".".join(parts[-2:])
        return ""

    @api.model
    def _parse_ga_session_id(self, cookie_value):
        """Extract session_id from ``_ga_XXXXXXXX`` cookie value.

        Cookie format: ``GS1.1.<session_ts>.<count>.<engaged>.<last_ts>.0.0.0``
        session_id = ``<session_ts>`` (third dot-separated component)
        """
        if not cookie_value:
            return ""
        parts = cookie_value.split(".")
        if len(parts) >= 3:
            return parts[2]
        return ""
