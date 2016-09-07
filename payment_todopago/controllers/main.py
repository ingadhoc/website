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


class TodoPagoController(http.Controller):
    _success_url = '/payment/todopago/success'
    _success_no_return_url = '/payment/todopago/success_no_return'
    _failure_no_return_url = '/payment/todopago/failure_no_return'
    _failure_url = '/payment/todopago/failure'
    _create_preference_url = '/payment/todopago/create_preference'

    @http.route([
        '/payment/todopago/create_preference',
    ],
        type='http', auth="none")
    def todopago_create_preference(self, **post):
        _logger.info(
            'todopago: create preference with post data %s',
            pprint.pformat(post))
        # TODO podriamos pasar cada elemento por separado para no necesitar
        # el literal eval
        todopago_data = literal_eval(post.get('todopago_data', {}))
        if not todopago_data:
            return werkzeug.utils.redirect("/")
        acquirer_id = todopago_data.get('acquirer_id')
        cr, uid, context = request.cr, SUPERUSER_ID, request.context
        request_url = request.registry[
            'payment.acquirer']._todopago_create_transaction(
            cr, uid, acquirer_id, post, context)
        return werkzeug.utils.redirect(request_url)

    def todopago_validate(self, **post):
        "Validate mercado pago payment from a return URL or IPN"
        _logger.info(
            'Validating todopago payment with post data %s',
            pprint.pformat(post))
        cr, uid, context = request.cr, SUPERUSER_ID, request.context
        request.registry['payment.transaction'].form_feedback(
            cr, uid, post, 'todopago', context)
        return None

    @http.route([
        '/payment/todopago/success_no_return',
    ],
        type='http', auth="none")
    def todopago_back_no_return(self, **post):
        """
        Odoo, si usas el boton de pago desde una sale order o email, no manda
        una return url, desde website si y la almacenan en un valor que vuelve
        desde el agente de pago. Como no podemos mandar esta "return_url" para
        que vuelva, directamente usamos dos distintas y vovemos con una u otra
        """
        # TODO nos falta implementar esto, en realidad deberia volver a la
        # orden de venta o a donde?
        _logger.info(
            'todopago: entering todopago no_return success with post data %s',
            pprint.pformat(post))
        self.todopago_validate(**post)
        cr, uid = request.cr, SUPERUSER_ID
        todopago_id = request.registry['payment.acquirer'].search(
            cr, uid, [('provider', '=', 'todopago')], limit=1)
        todopago = request.registry['payment.acquirer'].browse(
            cr, uid, todopago_id)
        return_url = '/'
        if todopago.todopago_success_return_url:
            return_url = todopago.todopago_success_return_url
        return werkzeug.utils.redirect(return_url)

    @http.route([
        '/payment/todopago/failure_no_return',
    ],
        type='http', auth="none")
    def todopago_back_no_return_failure(self, **post):
        """
        Odoo, si usas el boton de pago desde una sale order o email, no manda
        una return url, desde website si y la almacenan en un valor que vuelve
        desde el agente de pago. Como no podemos mandar esta "return_url" para
        que vuelva, directamente usamos dos distintas y vovemos con una u otra
        """
        # TODO nos falta implementar esto, en realidad deberia volver a la
        # orden de venta o a donde?
        _logger.info(
            'todopago: entering todopago no_return failure with post data %s',
            pprint.pformat(post))
        self.todopago_validate(**post)
        cr, uid = request.cr, SUPERUSER_ID
        todopago_id = request.registry['payment.acquirer'].search(
            cr, uid, [('provider', '=', 'todopago')], limit=1)
        todopago = request.registry['payment.acquirer'].browse(
            cr, uid, todopago_id)
        return_url = '/'
        if todopago.todopago_failure_return_url:
            return_url = todopago.todopago_failure_return_url
        return werkzeug.utils.redirect(return_url)

    @http.route([
        '/payment/todopago/failure',
    ],
        type='http', auth="public", website=True)
    def todopago_back_failure(self, **post):
        _logger.info(
            'todopago: entering todopago failure with post data %s',
            pprint.pformat(post))
        self.todopago_validate(**post)
        # buscamos la transaccion y mostramos el error
        reference = post.get('OPERATIONID')
        cr, uid, context = request.cr, SUPERUSER_ID, request.context
        transaction_id = request.registry['payment.transaction'].search(
            cr, uid, [('reference', '=', reference)], context=context)
        transaction = request.registry['payment.transaction'].browse(
            cr, uid, transaction_id, context=context)
        return request.website.render(
            "payment_todopago.payment_error", {'transaction': transaction})

    @http.route([
        '/payment/todopago/success',
    ],
        type='http', auth="none")
    def todopago_back_success(self, **post):
        # print '1111111111'
        _logger.info(
            'todopago: entering todopago success with post data %s',
            pprint.pformat(post))
        self.todopago_validate(**post)
        return werkzeug.utils.redirect('/shop/payment/validate')

    # @http.route([
    #     '/payment/todopago/failure'
    # ],
    #     type='http', auth="none")
    # def todopago_back_failure(self, **post):
    #     """
    #     If failure is return is because user has cancelled the payment
    #     if a collection_status has return, then we call todopago_validate
    #     to post payment failure reason.
    #     If no collection_status user has return before triying to pay
    #     """
    #     _logger.info(
    #         'todopago: entering todopago_back_failure with post data %s',
    #         pprint.pformat(post))
    #     # por ahora, para simplificar, siempre que se cancele devolvemos
    #     # a la pestana de pagos, ver observaciones de mas abajo
    #     return werkzeug.utils.redirect('/shop/payment')
        # # TODO para seguir con la logica de otros modulos deberiamos
        # # redirigir a la redirect url y que ahí decida que hacer
        # # el problema es que si gregresamos a esa url se nos esta limpiando
        # # el pedido
        # # return werkzeug.utils.redirect('/shop/payment/validate')
        # if post.get('collection_status') == 'null':
        #     return werkzeug.utils.redirect('/shop/payment')
        # self.todopago_validate(**post)
        # return werkzeug.utils.redirect('/shop/payment/validate')
