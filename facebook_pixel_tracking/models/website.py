from odoo import fields, models


class Website(models.Model):
    _inherit = "website"

    facebook_pixel_key = fields.Char("Facebook pixel ID")
