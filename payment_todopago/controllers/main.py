##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################

import logging
import pprint
import werkzeug
from odoo import http, SUPERUSER_ID
from odoo.http import request
from ast import literal_eval
_logger = logging.getLogger(__name__)


class TodoPagoController(http.Controller):
    _success_url = '/payment/todopago/success'
    _failure_url = '/payment/todopago/failure'
    _create_preference_url = '/payment/todopago/create_preference'

    @http.route([
        '/payment/todopago/create_preference',
    ],
        type='http', auth="none", csrf=False)
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
        '/payment/todopago/failure',
        '/payment/todopago/success',
    ],
        type='http', auth="public", csrf=False)
    def todopago_back_with_return(self, **post):
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
        return werkzeug.utils.redirect(transaction.todopago_Return_url or '/')
