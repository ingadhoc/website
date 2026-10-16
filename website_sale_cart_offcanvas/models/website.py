##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import fields, models


class Website(models.Model):
    _inherit = "website"

    # Odoo 20 dropped `add_to_cart_action`, the selection this used to extend, and moved
    # the choice to the "Add to cart" button of the builder. The panel keeps a site-wide
    # switch of its own so it can be turned off without uninstalling the module.
    cart_offcanvas_enabled = fields.Boolean(
        string="Cart Side Panel",
        default=True,
    )
