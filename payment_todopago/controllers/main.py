##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################

import logging
import pprint
import werkzeug

from odoo import http
from odoo.http import request
from odoo.tools.safe_eval import safe_eval

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
        # el safe_eval
        todopago_data = safe_eval(post.get('todopago_data', {}))
        if not todopago_data:
            return werkzeug.utils.redirect("/")
        acquirer_id = todopago_data.get('acquirer_id')
        request_url = request.env['payment.acquirer'].sudo().browse(
            acquirer_id)._todopago_create_transaction(post)
        return werkzeug.utils.redirect(request_url)

    def todopago_validate(self, **post):
        "Validate mercado pago payment from a return URL or IPN"
        _logger.info(
            'Validating todopago payment with post data %s',
            pprint.pformat(post))
        request.env['payment.transaction'].sudo().form_feedback(
            post, 'todopago')
        return None

    @http.route([
        '/payment/todopago/failure',
        '/payment/todopago/success',
    ],
        type='http', auth="public", csrf=False)
    def todopago_back_with_return(self, **post):
        _logger.info(
            'todopago: returning data %s',
            pprint.pformat(post))
        self.todopago_validate(**post)
        return werkzeug.utils.redirect("/payment/process")
