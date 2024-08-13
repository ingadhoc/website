##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields


class Website(models.Model):
    _inherit = 'website'

    force_sale_order_confirmation = fields.Boolean()
