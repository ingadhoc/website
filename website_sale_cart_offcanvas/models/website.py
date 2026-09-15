##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import fields, models


class Website(models.Model):
    _inherit = "website"

    add_to_cart_action = fields.Selection(
        selection_add=[("open_offcanvas", "Open cart panel")],
        ondelete={"open_offcanvas": "set default"},
    )
