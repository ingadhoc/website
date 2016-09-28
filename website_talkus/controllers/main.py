# -*- coding: utf-8 -*-
import openerp
from openerp.addons.web import http
from openerp.http import request
import random


class WebsiteChat(openerp.addons.web.controllers.main.Home):
    # Create the talkus website model.
    @http.route('/website_talkus/get_values',
                type='json', auth='public', website=True)
    def get_values(self):
        _object = request.registry["res.users"]
        obj = _object.browse(request.cr, request.uid, request.uid)

        webs_talkus_id = request.registry['website.talkus'].\
            search(request.cr, request.uid, [], limit=1)
        webs_talkus = request.registry['website.talkus'].\
            browse(request.cr, request.uid, webs_talkus_id)

        website_talkus = {'id': webs_talkus['id_talkus'],
                          'tag': webs_talkus['tag'],
                          # 'img': webs_talkus['loading_image'],
                          # 'backgroud_color': webs_talkus['backgroud_color'],
                          # 'border_color': webs_talkus['border_color'],
                          # 'welcomeMessage': webs_talkus['welcomeMessage'],
                          'login': obj.login,
                          }

        count_bubble = len(webs_talkus['bubble_ids'])
        if count_bubble > 0:
            count_bubble_r = random.randint(0, count_bubble - 1)
            bubble = webs_talkus['bubble_ids'][count_bubble_r]
            website_talkus['bubble'] = {
                'userName': bubble['userName'],
                'userPicture': bubble['userPicture'],
                'message': bubble['message'],
                # depreceated in new widget
                # 'welcomeMessage': bubble['welcomeMessage'],
                'delay': bubble['delay'],
            }
        return website_talkus
