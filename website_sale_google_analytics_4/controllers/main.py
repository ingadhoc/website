import logging

from odoo import http
from odoo.addons.website_sale.controllers.main import WebsiteSale

_logger = logging.getLogger(__name__)


class GA4WebsiteSale(WebsiteSale):
    @http.route()
    def shop_checkout(self, try_skip_step=None, **query_params):
        """Override to capture GA4 browser cookies into the sale order."""
        order = http.request.cart
        if order and not order.ga_client_id:
            try:
                cookies = http.request.httprequest.cookies
                website = http.request.website

                # --- Parse _ga cookie → client_id ---
                ga_cookie = cookies.get("_ga", "")
                client_id = order._parse_ga_client_id(ga_cookie)

                # --- Parse _ga_<container_id> cookie → session_id ---
                measurement_id = website.google_analytics_key or ""
                session_id = ""
                if measurement_id:
                    # G-ABCDEF1234 → cookie name _ga_ABCDEF1234
                    container_suffix = measurement_id.replace("G-", "")
                    session_cookie = cookies.get(f"_ga_{container_suffix}", "")
                    session_id = order._parse_ga_session_id(session_cookie)

                if client_id:
                    order.sudo().write(
                        {
                            "ga_client_id": client_id,
                            "ga_session_id": session_id or False,
                        }
                    )
            except Exception as exc:
                _logger.warning("GA4: failed to capture cookies: %s", exc)

        return super().shop_checkout(try_skip_step=try_skip_step, **query_params)
