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
        if not websites:
            return
        types = "\n".join(websites.sale_order_type_id.mapped("display_name"))
        # Only name the websites of the user's companies, but block for all of them
        visible_websites = websites.filtered(lambda w: w.company_id in self.env.companies)
        if visible_websites:
            raise UserError(
                self.env._(
                    "You cannot delete sale order type(s):\n%(types)s\nThey are used in website(s):\n%(websites)s",
                    types=types,
                    websites="\n".join(visible_websites.mapped("display_name")),
                )
            )
        raise UserError(
            self.env._(
                "You cannot delete sale order type(s):\n%(types)s\nThey are used in a website of another company.",
                types=types,
            )
        )
