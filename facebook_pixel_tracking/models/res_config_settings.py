from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    facebook_pixel_key = fields.Char(
        "Facebook pixel ID", related="website_id.facebook_pixel_key", readonly=False
    )
