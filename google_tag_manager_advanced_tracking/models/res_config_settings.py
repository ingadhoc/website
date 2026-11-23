##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    ga4_api_secret = fields.Char(
        string="GA4 API Secret",
        related="website_id.ga4_api_secret",
        readonly=False,
        groups="base.group_system",
    )
