##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models


class AccountMove(models.Model):
    _inherit = "account.move"

    def _post(self, soft=True):
        to_defer = self.env["account.move"]
        if self.env.context.get("website_force_background_post"):
            to_defer = self.filtered(lambda m: m.move_type == "out_invoice")
            to_defer.write({"background_post": True})
        return super(AccountMove, self - to_defer)._post(soft=soft)
