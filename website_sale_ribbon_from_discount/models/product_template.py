# -*- coding: utf-8 -*-

from odoo import models, fields

class PricelistItem(models.Model):
    _inherit = "product.template"

    ribbon_from_discount = fields.Many2one('product.ribbon', string='Ribbon from discount', readonly=True)