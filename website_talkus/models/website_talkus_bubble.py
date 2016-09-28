# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import fields, models


class website_talkus_bubble(models.Model):
    _name = 'website.talkus.bubble'
    _description = 'website.talkus.bubble'

    userName = fields.Char(
        'Name',
        required=True,
        help="User name displayed in the first welcome message",
    )
    userPicture = fields.Char(
        'User Picture',
        help="Url of the avatar displayed in the button near "
             "the bubble and in the first welcome message",
    )
    message = fields.Char(
        'message',
        help="Message displayed in the bubble",
    )
    # DEPRECEATED
    # welcomeMessage = fields.Char(
    #     'welcomeMessage',
    #     help="First welcome message displayed when "
    #          "the user open for live chat",
    # )
    delay = fields.Integer(
        'Delay',
        help="How many seconds before displaying the bubble",
    )
    website_talkus_id = fields.Many2one(
        'website.talkus',
        string='Website Talkus',
    )
