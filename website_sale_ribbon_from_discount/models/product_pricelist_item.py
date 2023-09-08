# -*- coding: utf-8 -*-

from odoo import models, fields

class PricelistItem(models.Model):
    _inherit = "product.pricelist.item"

    create_ribbon = fields.Boolean(string="Promocionar en eCommerce")
    website_ribbon_id = fields.Many2one('product.ribbon', string="Ribbon")