##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    website_sale_background_post = fields.Boolean(
        related="company_id.website_sale_background_post",
        readonly=False,
    )
