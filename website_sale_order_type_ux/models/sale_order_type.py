##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import api, models
from odoo.exceptions import UserError


class SaleOrderType(models.Model):
    _inherit = "sale.order.type"

    @api.ondelete(at_uninstall=False)
    def _unlink_except_used_in_website(self):
        # In 20 this also runs when another module is uninstalled
        if self.pool.uninstalling_modules:
            return
        websites = self.env["website"].sudo().search([("sale_order_type_id", "in", self.ids)])
        if websites:
            raise UserError(
                self.env._(
                    "You cannot delete sale order type(s):\n%(types)s\nThey are used in website(s):\n%(websites)s",
                    types="\n".join(websites.sale_order_type_id.mapped("display_name")),
                    websites="\n".join(websites.mapped("display_name")),
                )
            )
