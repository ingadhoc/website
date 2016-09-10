# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, fields


class product_template(models.Model):
    _inherit = 'product.template'

    website_promotion_id = fields.Many2one(
        'website.promotion',
        string='Website Promotion',
    )
