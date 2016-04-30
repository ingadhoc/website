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
    userName = fields.Char(
        'Name',
        required=True,
    )
    userPicture = fields.Char(
        'User',
    )
    message = fields.Char(
        'message',
    )
    welcomeMessage = fields.Char(
        'welcomeMessage',
    )
    loading_image = fields.Char(
        'Image',
    )
    tag = fields.Char(
        'Tag',
    )
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
