##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    cart_offcanvas_enabled = fields.Boolean(
        related="website_id.cart_offcanvas_enabled",
        readonly=False,
    )
