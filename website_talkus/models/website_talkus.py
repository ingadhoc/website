##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import fields, models


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
        help='Now Bubbles can be defined on talkus rules directly'
    )
    tag = fields.Char(
        'Tag',
    )
