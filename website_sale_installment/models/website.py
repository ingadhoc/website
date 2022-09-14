from odoo import fields, models


class Website(models.Model):

    _inherit = 'website'

    installment_price_id = fields.Many2one(
        'account.card.instalment',
        string='Second price',
    )


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    installment_price_id = fields.Many2one(
        'account.card.instalment',
        string='Second price',
        related='website_id.installment_price_id',
        readonly=False
    )
