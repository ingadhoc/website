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
from ast import literal_eval
_logger = logging.getLogger(__name__)
try:
    from mercadopago import mercadopago
except ImportError:
    _logger.debug('Cannot import external_dependency mercadopago')


class MercadoPagoController(http.Controller):
    _success_url = '/payment/mercadopago/success/'
    _success_no_return_url = '/payment/mercadopago/success_no_return/'
    _pending_url = '/payment/mercadopago/pending/'
    _pending_no_return_url = '/payment/mercadopago/pending_no_return/'
    _failure_url = '/payment/mercadopago/failure/'
    # _notify_url = '/payment/mercadopago/notify/'
    _create_preference_url = '/payment/mercadopago/create_preference'

    @http.route([
        '/payment/mercadopago/create_preference',
    ],
        type='http', auth="none", csrf=False)
    def mercadopago_create_preference(self, **post):
        _logger.info(
            'Mercadopago: create preference with post data %s',
            pprint.pformat(post))
        # TODO podriamos pasar cada elemento por separado para no necesitar
        # el literal eval
        mercadopago_data = literal_eval(post.get('mercadopago_data', {}))
        if not mercadopago_data:
            return werkzeug.utils.redirect("/")
        environment = mercadopago_data.get('environment')
        mercadopago_preference = mercadopago_data.get(
            'mercadopago_preference')
        mercadopago_client_id = mercadopago_data.get(
            'mercadopago_client_id')
        mercadopago_secret_key = mercadopago_data.get(
            'mercadopago_secret_key')
        if (
                not environment or
                not mercadopago_preference or
                not mercadopago_secret_key or
                not mercadopago_client_id
        ):
            _logger.warning('Missing parameters!')
            return werkzeug.utils.redirect("/")
        MPago = mercadopago.MP(
            mercadopago_client_id, mercadopago_secret_key)
        if environment == "prod":
            MPago.sandbox_mode(False)
        else:
            MPago.sandbox_mode(True)
        preferenceResult = MPago.create_preference(mercadopago_preference)
        _logger.info('Preference Result: %s' % preferenceResult)

        # # TODO validate preferenceResult response
        if environment == "prod":
            linkpay = preferenceResult['response']['init_point']
        else:
            linkpay = preferenceResult['response']['sandbox_init_point']

        return werkzeug.utils.redirect(linkpay)

    def mercadopago_validate(self, **post):
        "Validate mercado pago payment from a return URL or IPN"
        _logger.info(
            'Validating mercadopago payment with post data %s',
            pprint.pformat(post))
        cr, uid, context = request.cr, SUPERUSER_ID, request.context
        request.registry['payment.transaction'].form_feedback(
            cr, uid, post, 'mercadopago', context)
        return False

    @http.route([
        '/payment/mercadopago/success_no_return',
        '/payment/mercadopago/pending_no_return',
    ],
        type='http', auth="none", csrf=False)
    def mercadopago_back_no_return(self, **post):
        """
        Odoo, si usas el boton de pago desde una sale order o email, no manda
        una return url, desde website si y la almacenan en un valor que vuelve
        desde el agente de pago. Como no podemos mandar esta "return_url" para
        que vuelva, directamente usamos dos distintas y vovemos con una u otra
        """
        _logger.info(
            'Mercadopago: entering mecadopago_back with post data %s',
            pprint.pformat(post))
        self.mercadopago_validate(**post)
        return werkzeug.utils.redirect('/')

    @http.route([
        '/payment/mercadopago/success',
        '/payment/mercadopago/pending',
    ],
        type='http', auth="none", csrf=False)
    def mercadopago_back(self, **post):
        _logger.info(
            'Mercadopago: entering mecadopago_back with post data %s',
            pprint.pformat(post))
        self.mercadopago_validate(**post)
        return werkzeug.utils.redirect('/shop/payment/validate')

    @http.route([
        '/payment/mercadopago/failure'
    ],
        type='http', auth="none", csrf=False)
    def mercadopago_back_failure(self, **post):
        """
        If failure is return is because user has cancelled the payment
        if a collection_status has return, then we call mercadopago_validate
        to post payment failure reason.
        If no collection_status user has return before triying to pay
        """
        _logger.info(
            'Mercadopago: entering mercadopago_back_failure with post data %s',
            pprint.pformat(post))
        # por ahora, para simplificar, siempre que se cancele devolvemos
        # a la pestana de pagos, ver observaciones de mas abajo
        return werkzeug.utils.redirect('/shop/payment')
        # # TODO para seguir con la logica de otros modulos deberiamos
        # # redirigir a la redirect url y que ahí decida que hacer
        # # el problema es que si gregresamos a esa url se nos esta limpiando
        # # el pedido
        # # return werkzeug.utils.redirect('/shop/payment/validate')
        # if post.get('collection_status') == 'null':
        #     return werkzeug.utils.redirect('/shop/payment')
        # self.mercadopago_validate(**post)
        # return werkzeug.utils.redirect('/shop/payment/validate')

    # @http.route([
    #     '/payment/mercadopago/notify'
    #     ],
    #     type='http', auth="none")
    # def mercadopago_notify(self, **post):
    #     """
    #     This method is call when mercadopago notify us some event not in
    #     in the return url
    #     """
    #     self.mercadopago_validate(**post)
    #     return ''
