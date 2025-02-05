##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    cancel_old_website_quotations = fields.Boolean(
        config_parameter="website_sale_ux.cancel_old_website_quotations",
        help="Enable automatic cancellation of old website quotations.",
    )
