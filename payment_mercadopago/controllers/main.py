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
try:
    from mercadopago import mercadopago
except ImportError:
    _logger.debug('Cannot import external_dependency mercadopago')


class MercadoPagoController(http.Controller):
    _success_url = '/payment/mercadopago/success/'
    _pending_url = '/payment/mercadopago/pending/'
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
        mercadopago_data = safe_eval(post.get('mercadopago_data', {}))
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

    @http.route([
        '/payment/mercadopago/success',
        '/payment/mercadopago/pending',
        '/payment/mercadopago/failure'
    ],
        type='http', auth="none",
        # csrf=False,
        )
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
        request.env['payment.transaction'].sudo().form_feedback(
            post, 'mercadopago')
        return werkzeug.utils.redirect("/payment/process")
