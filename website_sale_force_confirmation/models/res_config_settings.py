##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    force_sale_order_confirmation = fields.Boolean(
        related='website_id.force_sale_order_confirmation',
        readonly=False,
    )
