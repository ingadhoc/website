from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    ip_address = fields.Char('ip_address', index=True, copy=False)
