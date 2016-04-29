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
    @http.route('/website_support_chat/get_values',
                type='json', auth='public', website=True)
    def get_values(self):
        _object = request.registry["res.users"]
        obj = _object.browse(request.cr, request.uid, request.uid)

        icp = request.registry['ir.config_parameter']
        webs_talkus_id = icp.get_param(request.cr, request.uid,
                                       'website_talkus')
        webs_talkus = request.registry['website.talkus'].\
            browse(request.cr,request.uid,int(webs_talkus_id))

        bubble = {'userName': webs_talkus['userName'],
                 'userPicture': webs_talkus['userPicture'],
                 'message': webs_talkus['message'],
                 'welcomeMessage': webs_talkus['welcomeMessage'],
                  }

        website_talkus = {'id': webs_talkus['id_talkus'],
                 'tag': webs_talkus['tag'],
                 'img': webs_talkus['loading_image'],
                 'login': obj.login,
                 'bubble': bubble,
                 }
        return website_talkus