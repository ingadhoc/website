from odoo import fields, models


class Website(models.Model):
    _inherit = "website"

    website_hide_all_prices = fields.Boolean(
        string="Hide all prices on website",
        copy=False,
        help="Hide all price at website level",
    )
