# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import fields, models


class website_talkus(models.Model):
    _name = 'website.talkus'
    _description = 'website.talkus.bubble'

    id_talkus = fields.Char(
        'Id talkus',
        required=True,
    )
    bubble_ids = fields.One2many(
        'website.talkus.bubble',
        'website_talkus_id',
        string='Bubbles',
    )
    welcomeMessage = fields.Char(
        'welcomeMessage',
        help="First welcome message displayed when "
             "the user open for live chat",
    )
    loading_image = fields.Char(
        'Image',
    )
    tag = fields.Char(
        'Tag',
    )
    backgroud_color = fields.Char(
        'Backgroud Color',
        help='Choose your color',
    )
    border_color = fields.Char(
        'Border Color',
        help='Choose your border_color',
    )
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
