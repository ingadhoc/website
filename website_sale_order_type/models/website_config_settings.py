# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields


class WebsiteConfigSettings(models.TransientModel):
    _inherit = 'website.config.settings'

    sale_order_type_id = fields.Many2one(
        'sale.order.type',
        related='website_id.sale_order_type_id',
        string='Sale Order Type',
    )
