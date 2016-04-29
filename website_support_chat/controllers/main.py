# -*- coding: utf-8 -*-
import openerp
from openerp.addons.web.controllers.main import WebClient
from openerp.addons.web import http
from openerp.http import request, STATIC_CACHE


class Website_Chat(openerp.addons.web.controllers.main.Home):
    #------------------------------------------------------
    # View
    #------------------------------------------------------

    #Create the talkus website model.
    @http.route('/website_support_chat/get_values', type='json', auth='public', website=True)
    def get_values(self):
        _object = request.registry["res.users"]
        obj = _object.browse(request.cr, request.uid, request.uid)

        icp = request.registry['ir.config_parameter']
        id_talkus = icp.get_param(request.cr, request.uid, 'website_talkus.id')
        tag_talkus = icp.get_param(request.cr, request.uid, 'website_talkus.tag')
        img_talkus = icp.get_param(request.cr, request.uid, 'website_talkus.loading_image')
        bubble_talkus_id = icp.get_param(request.cr, request.uid, 'website_talkus.bubble')
        bubble_talkus = request.registry['website.talkus.bubble'].browse(request.cr,request.uid,int(bubble_talkus_id))

        dic_bubble = {'userName':bubble_talkus['userName'],
                 'userPicture':bubble_talkus['userPicture'],
                 'message':bubble_talkus['message'],
                 'welcomeMessage':bubble_talkus['welcomeMessage'],
                 }
        return {
            'login': obj.login,
            'id': id_talkus,
            'tag': tag_talkus,
            'img': img_talkus,
            'bubble': dic_bubble,
        }


