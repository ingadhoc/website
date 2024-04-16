##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _cron_clean_old_quotations(self, website=None):
        website = bool(self.env['ir.config_parameter'].sudo().get_param('website_sale_ux.cancel_old_website_quotations', False))
        super()._cron_clean_old_quotations(website=website)
