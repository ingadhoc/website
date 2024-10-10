# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ProductRibbon(models.Model):
    _inherit = "product.ribbon"

    ribbon_from_discount = fields.Boolean("Ribbon creado desde un descuento")