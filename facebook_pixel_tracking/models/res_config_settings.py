from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    facebook_pixel_key = fields.Char("Facebook pixel ID", related="website_id.facebook_pixel_key", readonly=False)
    facebook_capi_access_token = fields.Char(
        string="Facebook CAPI Access Token",
        related="website_id.facebook_capi_access_token",
        readonly=False,
        groups="base.group_system",
    )
