##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, api, fields
import odoo.addons.decimal_precision as dp


class SaleOrderLine(models.Model):

    _inherit = 'sale.order.line'

    report_discount = fields.Float(
        compute='_compute_report_discount',
        digits=dp.get_precision('Discount')
    )

    @api.depends()
    def _compute_report_discount(self):
        for line in self:
            ret = 'total_excluded' if line.order_id.vat_discriminated \
                else 'total_included'
            discount = (line.price_unit *
                        (1.0 - (line.discount or 0.0) / 100.0))
            line.report_discount = line.tax_id.compute_all(
                discount, product=line.product_id,
                partner=line.order_id.partner_id)[ret]
