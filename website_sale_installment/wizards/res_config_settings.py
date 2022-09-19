from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    installment_price_ids = fields.Many2many(
        'account.card.installment',
        string='Installments',
        related='website_id.installment_price_ids',
        readonly=False
    )
