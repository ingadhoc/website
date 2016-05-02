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

        icp = request.registry['ir.config_parameter']
        webs_talkus_id = icp.get_param(request.cr, request.uid,
                                       'website_talkus')
        webs_talkus = request.registry['website.talkus'].\
            browse(request.cr, request.uid, int(webs_talkus_id))

        bubble = {'userName': '',
                  'userPicture': '',
                  'message': '',
                  'welcomeMessage': '',
                  'delay': 0,
                  }

        count_bubble = len(webs_talkus['bubble_ids'])
        if count_bubble > 0:
            count_bubble_r = random.randint(0, count_bubble-1)
            bubble = {'userName': webs_talkus['bubble_ids']
                      [count_bubble_r]['userName'],
                      'userPicture': webs_talkus['bubble_ids']
                      [count_bubble_r]['userPicture'],
                      'message': webs_talkus['bubble_ids']
                      [count_bubble_r]['message'],
                      'welcomeMessage': webs_talkus['bubble_ids']
                      [count_bubble_r]['welcomeMessage'],
                      'delay': webs_talkus['bubble_ids']
                      [count_bubble_r]['delay'],
                      }

        website_talkus = {'id': webs_talkus['id_talkus'],
                          'tag': webs_talkus['tag'],
                          'img': webs_talkus['loading_image'],
                          'backgroud_color': webs_talkus['backgroud_color'],
                          'border_color': webs_talkus['border_color'],
                          'login': obj.login,
                          'bubble': bubble,
                          }
        return website_talkus
