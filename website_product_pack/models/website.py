##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################

from odoo import api, models


class Website(models.Model):

    _inherit = 'website'

    @api.multi
    def sale_get_order(self, force_create=False, code=None,
                       update_pricelist=False, force_pricelist=False):
        self = self.with_context(
            from_cart=1,
            update_pricelist=update_pricelist,
        )
        res = super().sale_get_order(
            force_create=force_create, code=code,
            update_pricelist=update_pricelist, force_pricelist=force_pricelist)
        return res
