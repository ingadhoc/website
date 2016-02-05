# -*- coding: utf-8 -*-
from openerp import models, fields, api


class DeliveryCarrier(models.Model):
    _inherit = "delivery.carrier"

    only_published_for_group_ids = fields.Many2many(
        'res.groups',
        'delivery_carrier_group_rel',
        'carrier_id', 'group_id',
        string='Only Published for Groups',
        help='Set which groups are allowed to use this carrier. If no'
        ' group specified this carrier will be available for everybody'
        )


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model
    def _get_delivery_methods(self, order):
        carrier_ids = super(SaleOrder, self)._get_delivery_methods(order)
        carriers = self.env['delivery.carrier'].browse(carrier_ids)
        for carrier in carriers:
            if carrier.only_published_for_group_ids:
                if not set(self.env.user.groups_id.ids).intersection(
                        carrier.only_published_for_group_ids.ids):
                    carriers -= carrier
        return carriers.ids
