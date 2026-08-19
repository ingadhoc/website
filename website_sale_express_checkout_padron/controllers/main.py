##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
import logging
import socket

from odoo.addons.website_sale_express_checkout.controllers.main import (
    WebsiteSaleExpressCheckout,
)
from odoo.http import request

_logger = logging.getLogger(__name__)

# Keys of get_data_from_padron_afip()'s dict that we surface to the checkout.
_PADRON_FISCAL_FIELDS = (
    "name",
    "street",
    "city",
    "zip",
    "state_id",
    "l10n_ar_afip_responsibility_type_id",
)

_PADRON_TIMEOUT_PARAM = "website_sale_express_checkout.padron_timeout"
_DEFAULT_PADRON_TIMEOUT = 8.0
_CUIT_LENGTH = 11


class _PadronRollback(Exception):
    """Sentinel raised to force the lookup savepoint to roll back."""


class WebsiteSaleExpressCheckout(WebsiteSaleExpressCheckout):
    def _express_padron_lookup(self, vat=None):
        """Run the real ARCA padron query for a CUIT.

        Returns ``{"available": True, "found": True, "values": {...}}`` with the
        (possibly incomplete) fiscal fields ARCA returned, or ``{"available": True,
        "found": False}`` on any failure (missing certificate, WS timeout/error,
        CUIT absent from the padron) so the client lets the buyer fill the fields by
        hand. The client locks the returned fields and keeps the empty ones editable.
        """
        digits = "".join(ch for ch in (vat or "") if ch.isdigit())
        if len(digits) != _CUIT_LENGTH:
            return {"available": True, "found": False}

        env = request.env
        values = {}
        previous_timeout = socket.getdefaulttimeout()
        try:
            # The WS client does not expose a timeout, so we cap it at the socket
            # layer (best-effort); a hang surfaces as an exception caught below.
            socket.setdefaulttimeout(self._express_padron_timeout())
            # get_data_from_padron_afip has persistence side-effects (it creates
            # missing activity/tax records and, for real-estate/consorcio CUITs,
            # calls message_post on the partner — which fails on an in-memory NewId
            # record). Run it on a real partner inside a savepoint we always roll
            # back: nothing persists, but the method behaves exactly as it does
            # from the native "update from padron" wizard.
            with env.cr.savepoint():
                partner = (
                    env["res.partner"]
                    .sudo()
                    .create(
                        {
                            "name": "ARCA padron lookup",
                            "l10n_latam_identification_type_id": env.ref("l10n_ar.it_cuit").id,
                            "vat": digits,
                        }
                    )
                )
                values = partner.get_data_from_padron_afip()
                raise _PadronRollback()
        except _PadronRollback:
            pass  # values captured above; the savepoint has been rolled back
        except Exception as error:  # noqa: BLE001 - any failure -> manual entry
            _logger.warning("Express checkout: ARCA padron lookup failed for %s: %s", digits, error)
            return {"available": True, "found": False}
        finally:
            socket.setdefaulttimeout(previous_timeout)

        fiscal = {key: values[key] for key in _PADRON_FISCAL_FIELDS if values.get(key)}
        if fiscal:
            # ARCA answered with fiscal data (possibly incomplete: it may omit the
            # responsibility for some real-estate/special CUITs, or the city). The
            # client locks the fields ARCA returned and leaves the empty ones
            # editable, so a missing value never blocks the checkout.
            return {"available": True, "found": True, "values": fiscal}
        # ARCA did not answer with usable data -> fully manual entry.
        return {"available": True, "found": False}

    def _express_padron_timeout(self):
        raw = request.env["ir.config_parameter"].sudo().get_param(_PADRON_TIMEOUT_PARAM)
        try:
            return float(raw) if raw else _DEFAULT_PADRON_TIMEOUT
        except (TypeError, ValueError):
            return _DEFAULT_PADRON_TIMEOUT
