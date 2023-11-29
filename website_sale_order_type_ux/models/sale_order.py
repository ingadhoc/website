##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.depends("website_id", "partner_id", "company_id")
    @api.depends_context("partner_id", "company_id", "company")
    def _compute_sale_type_id(self):
        for record in self:
            sale_type = (
                record.partner_id.with_company(record.company_id).sale_type
                or record.partner_id.commercial_partner_id.with_company(
                    record.company_id
                ).sale_type
            )
            if not sale_type and record.website_id and record.website_id.sale_order_type_id:
                record.type_id = record.website_id.sale_order_type_id
            else:
                super(SaleOrder, record)._compute_sale_type_id()
