##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    enable_express_checkout = fields.Boolean(
        related="website_id.enable_express_checkout",
        readonly=False,
    )
