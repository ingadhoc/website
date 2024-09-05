from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    website_hide_all_prices = fields.Boolean(
        string="Hide all prices in ecommerce",
        readonly=False,
        related="website_id.website_hide_all_prices"
    )
