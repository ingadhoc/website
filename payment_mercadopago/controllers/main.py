# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################

try:
    import simplejson as json
except ImportError:
    import json
import logging
import pprint
import urllib2
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
        '/payment/mercadopago/failure'],
        type='http', auth="none")
    def mercadopago_back(self, **post):
        _logger.info(
            'Mercadopago: entering form_feedback with post data %s',
            pprint.pformat(post))
        cr, uid, context = request.cr, SUPERUSER_ID, request.context
        request.registry['payment.transaction'].form_feedback(
            cr, uid, post, 'mercadopago', context)
        return werkzeug.utils.redirect('/')
        # return werkzeug.utils.redirect()
    # @http.route('/payment/mercadopago/success', type='http', auth="none")
    # def mercadopago_success(self, **post):
        # """ MercadoPago Success """
        # _logger.info(
            # 'Beginning MercadoPago Success with post data %s',
            # pprint.pformat(post))
        # return_url = self._get_return_url(**post)
        # self.mercadopago_validate_data(**post)
        # return werkzeug.utils.redirect(return_url)

    # @http.route('/payment/mercadopago/pending', type='http', auth="none")
    # def mercadopago_pending(self, **post):
    #     """ MercadoPago Pending """
    #     _logger.info(
    #         'Beginning MercadoPago Pending with post data %s',
    #         pprint.pformat(post))

    # @http.route('/payment/mercadopago/failure', type='http', auth="none")
    # def mercadopago_failure(self, **post):
    #     """ MercadoPago Failure """
    #     # cr, uid, context = request.cr, SUPERUSER_ID, request.context
    #     _logger.info(
    #         'Beginning MercadoPago Failure with post data %s',
    #         pprint.pformat(post))
    #     # return_url = self._get_return_url(**post)
    #     # status = post.get('collection_status')
    #     # if status == 'null':
    #     #     post['collection_status'] = 'cancelled'
    #     # self.mercadopago_validate_data(**post)
    #     # return werkzeug.utils.redirect(return_url)
