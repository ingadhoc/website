# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import fields, models, api, tools, _
from erppeek import Client
from openerp.exceptions import Warning
import logging
_logger = logging.getLogger(__name__)


class website_talkus_bubble(models.Model):
    _name = 'website.talkus.bubble'
    _description = 'website.talkus.bubble'

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
   
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
