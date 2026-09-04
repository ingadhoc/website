import logging

from odoo import http
from odoo.addons.website_sale.controllers.main import WebsiteSale

_logger = logging.getLogger(__name__)


class FacebookCapiWebsiteSale(WebsiteSale):
    @http.route()
    def shop_checkout(self, try_skip_step=None, **query_params):
        """Override to capture Meta browser identifiers into the sale order.

        The purchase event is sent server-side at confirmation, which may
        arrive via a payment gateway webhook with no browser request. So the
        fbp/fbc/ip/user-agent/url are captured here, while the browser is
        still present, and persisted on the order.
        """
        order = http.request.cart
        if order:
            try:
                httprequest = http.request.httprequest
                cookies = httprequest.cookies

                # Fill each field only when still empty, so identifiers that
                # were not available on an earlier checkout render (e.g. the
                # _fbp cookie set later, or the pixel briefly blocked) are
                # captured on a subsequent render instead of frozen by a single
                # sentinel.
                vals = {}
                if not order.fb_fbp and cookies.get("_fbp"):
                    vals["fb_fbp"] = cookies.get("_fbp")
                if not order.fb_fbc:
                    fbc = cookies.get("_fbc")
                    if not fbc:
                        fbclid = query_params.get("fbclid")
                        if fbclid:
                            fbc = order._build_fbc_from_fbclid(fbclid)
                    if fbc:
                        vals["fb_fbc"] = fbc
                if not order.fb_client_ip_address and httprequest.remote_addr:
                    vals["fb_client_ip_address"] = httprequest.remote_addr
                if not order.fb_client_user_agent and httprequest.user_agent:
                    vals["fb_client_user_agent"] = httprequest.user_agent.string
                if not order.fb_event_source_url and httprequest.url:
                    vals["fb_event_source_url"] = httprequest.url

                if vals:
                    order.sudo().write(vals)
            except Exception as exc:
                _logger.warning("Facebook CAPI: failed to capture browser data: %s", exc)

        return super().shop_checkout(try_skip_step=try_skip_step, **query_params)
