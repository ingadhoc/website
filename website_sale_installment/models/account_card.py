from odoo import models


class AccountCard(models.Model):

    _inherit = ['account.card',  'website.published.multi.mixin']
    _name = 'account.card'

