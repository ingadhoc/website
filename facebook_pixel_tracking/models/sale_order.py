import hashlib
import json
import logging
import time
from functools import partial

import requests
from odoo import SUPERUSER_ID, api, fields, models
from odoo.modules.registry import Registry

_logger = logging.getLogger(__name__)

FACEBOOK_CAPI_ENDPOINT = "https://graph.facebook.com"
FACEBOOK_GRAPH_VERSION = "v23.0"
FACEBOOK_CAPI_TIMEOUT = 3  # seconds – must not block payment flow


class SaleOrder(models.Model):
    _inherit = "sale.order"

    fb_fbp = fields.Char(
        string="Facebook Browser ID (fbp)",
        help="Raw _fbp browser cookie captured at checkout start.",
        copy=False,
    )
    fb_fbc = fields.Char(
        string="Facebook Click ID (fbc)",
        help="Raw _fbc browser cookie (or built from the fbclid URL param) captured at checkout start.",
        copy=False,
    )
    fb_client_ip_address = fields.Char(
        string="Facebook Client IP",
        help="Client IP captured at checkout start (required by Meta for web events).",
        copy=False,
    )
    fb_client_user_agent = fields.Char(
        string="Facebook Client User Agent",
        help="Client user-agent captured at checkout start (required by Meta for web events).",
        copy=False,
    )
    fb_event_source_url = fields.Char(
        string="Facebook Event Source URL",
        help="Checkout URL captured at checkout start (required by Meta for web events).",
        copy=False,
    )
    facebook_capi_pending_payload = fields.Json(
        string="Facebook CAPI Pending Payload",
        help="Stores a failed Conversions API payload for retry by the scheduled action.",
        copy=False,
    )
    facebook_capi_purchase_sent = fields.Boolean(
        string="Facebook CAPI Purchase Sent",
        help="Set once the server-side Purchase event has been accepted by Meta, "
        "so a cancel + re-confirm does not report the same order twice.",
        copy=False,
    )

    # ------------------------------------------------------------------
    # Payload builders
    # ------------------------------------------------------------------

    def _prepare_facebook_capi_custom_data(self):
        """Return a Meta CAPI ``custom_data`` dict for this order.

        Built directly from the order lines – not from the shared
        ``prepare_purchase_information`` helper, whose return type varies by
        which tracking modules are installed (``website_sale_advanced_tracking``
        returns a JSON string, ``website_sale_google_analytics_4`` overrides the
        same method returning a dict). All ``content_ids``/``id`` are emitted as
        strings: if the browser sends ``['1234']`` and the server ``[1234]``
        Meta treats the events as different and deduplication breaks silently.
        """
        self.ensure_one()
        contents = []
        content_ids = []
        for line in self.order_line:
            if getattr(line, "is_delivery", False) or getattr(line, "is_reward_line", False):
                continue
            item_id = str(line.product_id.default_code or line.product_id.id)
            content_ids.append(item_id)
            contents.append(
                {
                    "id": item_id,
                    "quantity": line.product_uom_qty,
                    "item_price": line.price_reduce_taxinc,
                }
            )
        return {
            "value": self.amount_total,
            "currency": self.currency_id.name,
            "content_type": "product",
            "content_ids": content_ids,
            "contents": contents,
            "order_id": str(self.id),
        }

    def _prepare_facebook_capi_user_data(self):
        """Build the Meta CAPI ``user_data`` dict from the order partner.

        Personal identifiers are SHA-256 hashed over their normalized
        (lowercase + trim) value; browser signals (fbp/fbc/ip/user agent)
        are sent raw. Empty values are omitted, never sent blank.
        """
        self.ensure_one()
        user_data = {}

        def add_hashed(key, value):
            hashed = self._facebook_hash(value)
            if hashed:
                user_data[key] = hashed

        partner = self.partner_id
        if partner:
            add_hashed("em", partner.email)
            add_hashed("ph", self._facebook_normalize_phone(partner.phone))
            # Only split first/last name for individuals; a company name hashed
            # as fn/ln would send misleading person-shaped signals to Meta.
            if not partner.is_company:
                name = (partner.name or "").strip()
                if name:
                    parts = name.split(" ", 1)
                    add_hashed("fn", parts[0])
                    if len(parts) > 1:
                        add_hashed("ln", parts[1])
            add_hashed("ct", partner.city)
            if partner.state_id:
                add_hashed("st", partner.state_id.code or partner.state_id.name)
            add_hashed("zp", partner.zip)
            if partner.country_id:
                add_hashed("country", partner.country_id.code)
            add_hashed("external_id", str(partner.id))

        if self.fb_fbp:
            user_data["fbp"] = self.fb_fbp
        if self.fb_fbc:
            user_data["fbc"] = self.fb_fbc
        if self.fb_client_ip_address:
            user_data["client_ip_address"] = self.fb_client_ip_address
        if self.fb_client_user_agent:
            user_data["client_user_agent"] = self.fb_client_user_agent
        return user_data

    # ------------------------------------------------------------------
    # Conversions API
    # ------------------------------------------------------------------

    def _send_facebook_capi_event(self, event_name, custom_data, _is_retry=False, event_time=None):
        """Send a single event to the Meta Conversions API.

        Returns True on success, False on failure. On failure the payload is
        persisted in ``facebook_capi_pending_payload`` for later retry by the
        cron (unless this call IS the retry). ``event_time`` is preserved
        across retries so the cron can discard events older than 7 days.
        """
        self.ensure_one()
        # Only website (ecommerce) orders emit a "website" Purchase; skip
        # backend/manual/subscription orders so they don't inflate reporting.
        if not self.website_id:
            if _is_retry:
                self._facebook_capi_bump_retry_attempts()
            return False
        # Meta rejects action_source="website" events without a user agent.
        # Only send when browser identity was captured at checkout (mirrors the
        # ga_client_id guard of website_sale_google_analytics_4); this avoids a
        # guaranteed HTTP 400 (and endless retries) for orders that skipped the
        # checkout page, e.g. express checkout.
        if not self.fb_client_user_agent:
            if _is_retry:
                self._facebook_capi_bump_retry_attempts()
            return False
        website = self.website_id.sudo()
        pixel_id = website.facebook_pixel_key
        access_token = website.facebook_capi_access_token

        if not pixel_id or not access_token:
            if _is_retry:
                self._facebook_capi_bump_retry_attempts()
            return False

        if event_time is None:
            event_time = int(time.time())

        # The whole build + HTTP is inside the try so this method never raises:
        # a bad partner value (user_data hashing, json.dumps) must persist a
        # pending payload like any other failure, not propagate out and abort a
        # batch caller (the retry cron loop has no per-order guard of its own).
        try:
            event = {
                "event_name": event_name,
                "event_time": event_time,
                "action_source": "website",
                "event_id": str(self.id),
                "user_data": self._prepare_facebook_capi_user_data(),
                "custom_data": custom_data,
            }
            if self.fb_event_source_url:
                event["event_source_url"] = self.fb_event_source_url

            # access_token travels in the request body (not the URL query string)
            # so the secret can never leak via the URL into proxy or access logs.
            form_data = {"data": json.dumps([event]), "access_token": access_token}
            test_event_code = (
                self.env["ir.config_parameter"].sudo().get_param("facebook_pixel_tracking.test_event_code")
            )
            if test_event_code:
                form_data["test_event_code"] = test_event_code

            url = "%s/%s/%s/events" % (FACEBOOK_CAPI_ENDPOINT, FACEBOOK_GRAPH_VERSION, pixel_id)
            response = requests.post(url, data=form_data, timeout=FACEBOOK_CAPI_TIMEOUT)
            response.raise_for_status()
            _logger.info(
                "Facebook CAPI event '%s' sent for order %s",
                event_name,
                self.name,
            )
            # A previous attempt may have queued this order for retry; clear it.
            if self.facebook_capi_pending_payload:
                self.facebook_capi_pending_payload = False
            if event_name == "Purchase":
                self.facebook_capi_purchase_sent = True
            return True
        except Exception as exc:
            # Log a sanitized detail (status + Meta error body), never ``exc``
            # or the URL, as an extra guard around the secret token.
            error_response = getattr(exc, "response", None)
            if error_response is not None:
                detail = "HTTP %s: %s" % (error_response.status_code, (error_response.text or "")[:200])
            else:
                detail = type(exc).__name__
            _logger.warning(
                "Facebook CAPI event '%s' failed for order %s: %s",
                event_name,
                self.name,
                detail,
            )
            if not _is_retry:
                attempts = (self.facebook_capi_pending_payload or {}).get("_attempts", 0)
                self.facebook_capi_pending_payload = {
                    "event_name": event_name,
                    "custom_data": custom_data,
                    "event_time": event_time,
                    "_attempts": attempts + 1,
                }
            else:
                self._facebook_capi_bump_retry_attempts()
            return False

    def _facebook_capi_bump_retry_attempts(self):
        """Increment the retry counter on the pending payload.

        Called on any failed retry (including config now missing) so a
        permanently unsendable order still converges to max_attempts and gets
        discarded by the cron, instead of being retried forever. Only invoked
        on the retry path, where a pending payload already exists.
        """
        self.ensure_one()
        payload = dict(self.facebook_capi_pending_payload or {})
        payload["_attempts"] = payload.get("_attempts", 0) + 1
        self.facebook_capi_pending_payload = payload

    # ------------------------------------------------------------------
    # Confirmation hook – server-side purchase event
    # ------------------------------------------------------------------

    def _action_confirm(self):
        """Queue a server-side Purchase event to Meta after confirmation.

        The actual HTTP call is deferred to a post-commit hook so that (a) a
        rolled-back confirmation never reports a phantom Purchase, and (b) the
        external call never holds row locks on ``sale.order`` while a batch of
        orders is being confirmed. Covers both the synchronous confirmation and
        the one that arrives via a payment gateway webhook (no browser request).
        """
        res = super()._action_confirm()
        # Skip orders already sent, and orders that still have a queued payload
        # (the retry cron owns those) so a cancel + re-confirm does not double-send.
        orders = self.filtered(
            lambda o: o.website_id
            and o.fb_client_user_agent
            and not o.facebook_capi_purchase_sent
            and not o.facebook_capi_pending_payload
        )
        if orders:
            self.env.cr.postcommit.add(partial(self._facebook_capi_send_purchase_postcommit, orders.ids))
        return res

    def _facebook_capi_send_purchase_postcommit(self, order_ids):
        """Send the queued Purchase event(s) after the confirmation commits.

        Runs in a fresh cursor because the original transaction is already
        committed by the time post-commit callbacks fire.
        """
        dbname = self.env.cr.dbname
        # Fresh cursor because the confirmation transaction is already committed
        # by the time post-commit callbacks fire (the context manager commits on
        # clean exit, so the pending-payload / sent-flag writes persist). As
        # SUPERUSER because website checkouts confirm as the public/portal user,
        # which cannot read the order or its partner.
        with Registry(dbname).cursor() as cr:
            env = api.Environment(cr, SUPERUSER_ID, {})
            for order in env["sale.order"].browse(order_ids).exists():
                try:
                    order._send_facebook_capi_event("Purchase", order._prepare_facebook_capi_custom_data())
                except Exception as exc:
                    _logger.warning(
                        "Facebook CAPI purchase event skipped for order %s: %s",
                        order.id,
                        exc,
                    )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @api.model
    def _facebook_hash(self, value):
        """Return the SHA-256 hex digest of the normalized value, or ''."""
        if not value:
            return ""
        normalized = str(value).strip().lower()
        if not normalized:
            return ""
        return hashlib.sha256(normalized.encode("utf-8")).hexdigest()

    @api.model
    def _facebook_normalize_phone(self, phone):
        """Keep only digits (Meta expects the number with country code, no symbols)."""
        if not phone:
            return ""
        return "".join(ch for ch in phone if ch.isdigit())

    @api.model
    def _build_fbc_from_fbclid(self, fbclid, creation_time_ms=None):
        """Build an fbc value from an ``fbclid`` URL param (Meta documented format).

        Format: ``fb.1.<creation_time_ms>.<fbclid>``.
        """
        if not fbclid:
            return ""
        if creation_time_ms is None:
            creation_time_ms = int(time.time() * 1000)
        return "fb.1.%s.%s" % (creation_time_ms, fbclid)
