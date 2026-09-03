##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import fields, models


class Website(models.Model):
    _inherit = "website"

    # Campo "dummy" (placeholder): en v18 solo almacena el valor. La integración
    # GA4 server-side que lo consume vive en v19 (module website_sale_google_analytics_4,
    # que define este mismo campo homónimo). Se agrega acá para que los clientes en
    # v18 puedan generar y cargar su GA4 API Secret antes del pase de versión; el
    # Upgrade Line de deprecación de GTM migra el valor al módulo nuevo. Ver tarea #66923.
    ga4_api_secret = fields.Char(
        string="GA4 API Secret",
        copy=False,
        groups="base.group_system",
        help=(
            "Measurement Protocol API Secret generated in GA4 admin.\n"
            "Required to send server-side events (purchase, refund) after upgrading to v19.\n"
            "Generate one at: Admin → Data Streams → your stream → Measurement Protocol API secrets."
        ),
    )
