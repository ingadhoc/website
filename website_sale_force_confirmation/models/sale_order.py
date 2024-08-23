##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_quotation_sent(self):
        orders_from_website = self.filtered(lambda x: x.website_id and x.website_id.force_sale_order_confirmation)
        if orders_from_website:
            orders_from_website.action_confirm()
        super(SaleOrder, self - orders_from_website).action_quotation_sent()
