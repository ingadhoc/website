##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    @api.model
    def _inverse_account_on_checkout(self):
        for record in self:
            if not record.website_id:
                continue
            record.website_id.account_on_checkout = record.account_on_checkout
            # account_on_checkout implies different values for `auth_signup_uninvited
            if record.account_on_checkout == 'disabled':
                record.website_id.auth_signup_uninvited = 'b2b'
