# -*- coding: utf-'8' "-*-"
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################

try:
    import simplejson as json
except ImportError:
    import json
import logging
import urlparse
from openerp.addons.payment.models.payment_acquirer import ValidationError
from openerp.addons.payment_mercadopago.controllers.main import (
    MercadoPagoController)
from openerp import api, fields, models, _
from openerp.addons.payment_mercadopago.mercadopago import mercadopago

_logger = logging.getLogger(__name__)


class AcquirerMercadopago(models.Model):
    _inherit = 'payment.acquirer'

    @api.model
    def _get_mercadopago_urls(self, environment):
        """ MercadoPago URLS """
        if environment == 'prod':
            return {
                'mercadopago_form_url': (
                    'https://www.mercadopago.com/mla/checkout/pay'),
                # 'mercadopago_rest_url': (
                #     'https://api.mercadolibre.com/oauth/token'),
            }
        else:
            return {
                'mercadopago_form_url': (
                    'https://sandbox.mercadopago.com/mla/checkout/pay'),
                # 'mercadopago_rest_url': (
                #     'https://api.sandbox.mercadolibre.com/oauth/token'),
            }

    @api.model
    def _get_providers(self):
        providers = super(AcquirerMercadopago, self)._get_providers()
        providers.append(['mercadopago', 'MercadoPago'])
        return providers

    mercadopago_client_id = fields.Char(
        'MercadoPago Client Id',
        required_if_provider='mercadopago',
        help='Visit https://www.mercadopago.com/mla/account/credentials to get'
        ' this parameter',
        )
    mercadopago_secret_key = fields.Char(
        'MercadoPago Secret Key',
        required_if_provider='mercadopago',
        help='Visit https://www.mercadopago.com/mla/account/credentials to get'
        ' this parameter',
        )

    @api.multi
    def mercadopago_compute_fees(self, amount, currency_id, country_id):
        """ Compute mercadopago fees.

            :param float amount: the amount to pay
            :param integer country_id: an ID of a res.country, or None. This is
                                       the customer's country, to be compared
                                       to the acquirer company country.
            :return float fees: computed fees
        """
        self.ensure_one()
        if not self.fees_active:
            return 0.0
        country = self.env['res.country'].browse(country_id)
        if country and self.company_id.country_id.id == country.id:
            percentage = self.fees_dom_var
            fixed = self.fees_dom_fixed
        else:
            percentage = self.fees_int_var
            fixed = self.fees_int_fixed
        fees = (percentage / 100.0 * amount + fixed) / (1 - percentage / 100.0)
        return fees

    @api.multi
    def mercadopago_form_generate_values(self, partner_values, tx_values):
        self.ensure_one()
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')

        if not self.mercadopago_client_id or not self.mercadopago_secret_key:
            raise ValidationError(_(
                'YOU MUST COMPLETE acquirer.mercadopago_client_id and '
                'acquirer.mercadopago_secret_key'))

        MPago = mercadopago.MP(
            self.mercadopago_client_id, self.mercadopago_secret_key)

        if self.environment == "prod":
            MPago.sandbox_mode(False)
        else:
            MPago.sandbox_mode(True)

        preference = {
            "items": [{
                "title": "Orden Ecommerce " + tx_values["reference"],
                "quantity": 1,
                "currency_id": (
                    tx_values['currency'] and
                    tx_values['currency'].name or ''),
                "unit_price": tx_values["amount"],
                }],
            "payer": {
                "name": partner_values["name"],
                "surname": partner_values["first_name"],
                "email": partner_values["email"],
                },
            "back_urls": {
                "success": '%s' % urlparse.urljoin(
                    base_url, MercadoPagoController._success_url),
                "failure": '%s' % urlparse.urljoin(
                    base_url, MercadoPagoController._failure_url),
                "pending": '%s' % urlparse.urljoin(
                    base_url, MercadoPagoController._pending_url)
                },
            # TODO implementar notification_url, mas codigo en commits
            # anteriores
            # "notification_url": '%s' % urlparse.urljoin(
            #     base_url, MercadoPagoController._notify_url),
            "auto_return": "approved",
            "external_reference": tx_values["reference"],
            "expires": False,
            }

        preferenceResult = MPago.create_preference(preference)

        _logger.info('Preference Result: %s' % preferenceResult)
        if 'response' in preferenceResult:
            if 'id' in preferenceResult['response']:
                MPagoPrefId = preferenceResult['response']['id']
        else:
            error_msg = 'Returning response is:'
            error_msg += json.dumps(preferenceResult, indent=2)
            _logger.error(error_msg)
            raise ValidationError(error_msg)

        mercadopago_tx_values = dict(tx_values)
        # we return this pref_id that is used to go to the payment with
        # mercadopago button
        if MPagoPrefId:
            mercadopago_tx_values.update({
                'pref_id': MPagoPrefId,
            })
        print 'mercadopago_tx_values', mercadopago_tx_values
        return partner_values, mercadopago_tx_values

    @api.multi
    def mercadopago_get_form_action_url(self):
        self.ensure_one()
        mercadopago_urls = self._get_mercadopago_urls(
            self.environment)['mercadopago_form_url']
        _logger.info("mercadopago_get_form_action_url: %s" % mercadopago_urls)
        return mercadopago_urls


class TxMercadoPago(models.Model):
    _inherit = 'payment.transaction'

    mercadopago_txn_id = fields.Char(
        'Transaction ID'
        )
    mercadopago_txn_type = fields.Char(
        'Transaction type',
        help='Informative field computed after payment',
        )

    @api.model
    def _mercadopago_form_get_tx_from_data(self, data):
        reference = data.get('external_reference')
        collection_id = data.get('collection_id')
        if not reference or not collection_id:
            error_msg = (
                'MercadoPago: received data with missing reference (%s) or '
                'collection_id (%s)' % (reference, collection_id))
            _logger.error(error_msg)
            raise ValidationError(error_msg)

        # find tx -> @TDENOTE use txn_id ?
        txs = self.env['payment.transaction'].search(
            [('reference', '=', reference)])
        if not txs or len(txs) > 1:
            error_msg = (
                'MercadoPago: received data for reference %s' % (reference))
            if not txs:
                error_msg += '; no order found'
            else:
                error_msg += '; multiple order found'
            _logger.error(error_msg)
            raise ValidationError(error_msg)
        return txs[0]

    @api.model
    def _mercadopago_form_get_invalid_parameters(self, tx, data):
        invalid_parameters = []
        # TODO invalid paramters
        # if data.get('pspReference'):
        # _logger.warning('Received a notification from MercadoLibre.')
        return invalid_parameters

    @api.model
    def _mercadopago_form_validate(self, tx, data):
        """
        From:
        https://developers.mercadopago.com/documentacion/notificaciones-de-pago
        """
        status = data.get('collection_status')
        data = {
            'acquirer_reference': data.get('external_reference'),
            'mercadopago_txn_type': data.get('payment_type'),
            'mercadopago_txn_id': data.get('merchant_order_id', False),
            # otros parametros que vuevlven son 'collection_id'
        }
        if status in ['approved', 'processed']:
            _logger.info(
                'Validated MercadoPago payment for tx %s: set as done' % (
                    tx.reference))
            data.update(
                state='done',
                date_validate=data.get('payment_date', fields.datetime.now()))
            return tx.write(data)
        elif status in ['pending', 'in_process', 'in_mediation']:
            _logger.info(
                'Received notification for MercadoPago payment %s: set as '
                'pending' % (tx.reference))
            data.update(
                state='pending',
                state_message=data.get('pending_reason', ''))
            return tx.write(data)
        elif status in ['cancelled', 'refunded', 'charged_back', 'rejected']:
            _logger.info(
                'Received notification for MercadoPago payment %s: '
                'set as cancelled' % (tx.reference))
            data.update(
                state='cancel',
                state_message=data.get('cancel_reason', ''))
            return tx.write(data)
        else:
            error = (
                'Received unrecognized status for MercadoPago payment %s: %s, '
                'set as error' % (tx.reference, status))
            _logger.info(error)
            data.update(state='error', state_message=error)
            return tx.write(data)
