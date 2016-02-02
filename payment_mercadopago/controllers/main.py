# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################

import logging
import pprint
import werkzeug

from openerp import http, SUPERUSER_ID
from openerp.http import request

_logger = logging.getLogger(__name__)


class MercadoPagoController(http.Controller):
    _success_url = '/payment/mercadopago/success/'
    _pending_url = '/payment/mercadopago/pending/'
    _failure_url = '/payment/mercadopago/failure/'

    @http.route([
        '/payment/mercadopago/success',
        '/payment/mercadopago/pending',
        ],
        type='http', auth="none")
    def mercadopago_back(self, **post):
        _logger.info(
            'Mercadopago: entering form_feedback with post data %s',
            pprint.pformat(post))
        cr, uid, context = request.cr, SUPERUSER_ID, request.context
        request.registry['payment.transaction'].form_feedback(
            cr, uid, post, 'mercadopago', context)
        # de alguna manera esta url deberia obtenerse de esta manera pero
        # por alguna razon no llega
        # return werkzeug.utils.redirect(post.pop('return_url', '/'))
        return werkzeug.utils.redirect('/shop/payment/validate')

    @http.route([
        '/payment/mercadopago/failure'
        ],
        type='http', auth="none")
    def mercadopago_back_failure(self, **post):
        _logger.info(
            'Mercadopago: entering form_feedback with post data %s',
            pprint.pformat(post))
        cr, uid, context = request.cr, SUPERUSER_ID, request.context
        # si volvemos con regresar, entonces llega null, lo cambiamos por
        # cancelled
        if post.get('collection_status') == 'null':
            post['collection_status'] = 'cancelled'
        request.registry['payment.transaction'].form_feedback(
            cr, uid, post, 'mercadopago', context)
        return werkzeug.utils.redirect('/shop/payment')
