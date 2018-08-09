##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
import logging
from odoo.addons.payment.models.payment_acquirer import ValidationError
from odoo import api, fields, models
_logger = logging.getLogger(__name__)


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
    def _mercadopago_form_get_invalid_parameters(self, data):
        invalid_parameters = []
        # TODO implementar invalid paramters desde
        # https://www.mercadopago.com.ar/developers/es/api-docs/
        # basic-checkout/checkout-preferences/
        # if data.get('pspReference'):
        # _logger.ValidationError('Received a notification from MercadoLibre.')
        return invalid_parameters

    @api.model
    def _mercadopago_form_validate(self, data):
        """
        From:
        https://developers.mercadopago.com/documentacion/notificaciones-de-pago
        Por lo que vi nunca se devuelve la "cancel_reason" o "pending_reason"
        """
        tx = self
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
