import logging

import requests
from odoo import fields, models

_logger = logging.getLogger(__name__)

GA4_MP_ENDPOINT = "https://www.google-analytics.com/mp/collect"
GA4_MP_TIMEOUT = 3


class AccountMove(models.Model):
    _inherit = "account.move"

    ga4_mp_pending_payload = fields.Json(
        string="GA4 MP Pending Payload",
        help="Stores a failed refund Measurement Protocol payload for retry.",
        copy=False,
    )

    # ------------------------------------------------------------------
    # Post hook – server-side refund event
    # ------------------------------------------------------------------

    def _post(self, soft=True):
        res = super()._post(soft=soft)
        for move in res.filtered(lambda m: m.move_type == "out_refund"):
            try:
                move._send_ga4_mp_refund()
            except Exception as exc:
                _logger.warning(
                    "GA4 MP refund event skipped for move %s: %s",
                    move.name,
                    exc,
                )
        return res

    def _get_ga4_refund_items(self, sale_order):
        """Return the refunded items, described as the purchase event described them.

        Each credit note line is mapped back to its sale order line so the
        item data comes from the same core helper the purchase event uses:
        a product reported under one id when bought and another when
        refunded leaves the two events unrelated in GA4.
        """
        self.ensure_one()
        items = []
        for line in self.invoice_line_ids.filtered(lambda l: l.product_id and not l.display_type):
            sale_line = line.sale_line_ids.filtered(lambda sl: not sl.is_delivery)[:1]
            if not sale_line:
                continue
            items.append(
                {
                    **sale_order._get_order_line_tracking_data(sale_line),
                    "quantity": abs(line.quantity),
                }
            )
        return items

    def _send_ga4_mp_refund(self, _is_retry=False):
        """Send a ``refund`` Measurement Protocol event for this credit note.

        Returns True on success, False on failure.
        """
        self.ensure_one()
        # Locate the originating sale order for GA session data.
        # Prefer the direct relationship via invoice lines (most reliable), then
        # fall back to invoice_origin string match filtered by company to avoid
        # cross-company or multi-origin false matches.
        sale_order = self.invoice_line_ids.sale_line_ids.order_id.filtered(lambda o: o.company_id == self.company_id)[
            :1
        ]
        if not sale_order:
            sale_order = (
                self.env["sale.order"]
                .sudo()
                .search(
                    [("name", "=", self.invoice_origin), ("company_id", "=", self.company_id.id)],
                    limit=1,
                )
            )
        if not sale_order or not sale_order.ga_client_id:
            return False

        website = (sale_order.website_id or self.env["website"].get_current_website()).sudo()
        measurement_id = sale_order._get_ga4_measurement_id()
        api_secret = website.ga4_api_secret
        if not measurement_id or not api_secret:
            return False

        params = {
            # Same id the purchase event reported, so GA4 ties the refund to it.
            "transaction_id": sale_order.name,
            "value": abs(self.amount_untaxed),
            "tax": abs(self.amount_tax),
            "currency": self.currency_id.name,
            "items": self._get_ga4_refund_items(sale_order),
        }
        if sale_order.ga_session_id:
            params["session_id"] = sale_order.ga_session_id
        params["engagement_time_msec"] = 100

        body = {
            "client_id": sale_order.ga_client_id,
            "events": [{"name": "refund", "params": params}],
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
                "GA4 MP 'refund' event sent for move %s (origin order %s)",
                self.name,
                sale_order.name,
            )
            return True
        except Exception as exc:
            _logger.warning(
                "GA4 MP refund event failed for move %s (origin order %s): %s",
                self.name,
                sale_order.name,
                exc,
            )
            if not _is_retry:
                attempts = (self.ga4_mp_pending_payload or {}).get("_attempts", 0)
                self.ga4_mp_pending_payload = {
                    "_attempts": attempts + 1,
                }
            else:
                payload = dict(self.ga4_mp_pending_payload or {})
                payload["_attempts"] = payload.get("_attempts", 0) + 1
                self.ga4_mp_pending_payload = payload
            return False
