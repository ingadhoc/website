from odoo import fields, models


class Website(models.Model):

    _inherit = 'website'

    installment_price_ids = fields.Many2many(
        'account.card.installment',
        string='Installments',
    )
