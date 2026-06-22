##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import _, models
from odoo.exceptions import UserError


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def _check_amls_exigibility_for_reconciliation(self, shadowed_aml_values=None):
        # When reconciling as part of a background-post flow, the invoice is still
        # in draft because action_post was deferred. Allow reconciliation with draft
        # lines — the cron will post the invoice later, at which point the partial
        # reconcile will still be valid since line amounts are already final.
        if self.env.context.get("website_force_background_post"):
            if any(aml.reconciled for aml in self):
                raise UserError(_("You are trying to reconcile some entries that are already reconciled."))
            if any(aml.parent_state == "cancel" for aml in self):
                raise UserError(_("You can only reconcile posted entries."))
            return
        return super()._check_amls_exigibility_for_reconciliation(shadowed_aml_values)
