from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    out_of_stock_display = fields.Selection(related="website_id.out_of_stock_display", readonly=False, required=True)
