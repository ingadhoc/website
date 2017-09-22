# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, fields


class WebsiteConfigSettings(models.TransientModel):
    _inherit = 'website.config.settings'

    sale_order_type_id = fields.Many2one(
        'sale.order.type',
        related='website_id.sale_order_type_id',
        string='Sale Order Type',
    )
