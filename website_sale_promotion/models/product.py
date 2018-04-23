# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields


class product_template(models.Model):
    _inherit = 'product.template'

    website_promotion_id = fields.Many2one(
        'website.promotion',
        string='Website Promotion',
    )
