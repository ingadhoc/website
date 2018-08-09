##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
import logging

from odoo import api, fields, models
from odoo.addons.payment.models.payment_acquirer import ValidationError

_logger = logging.getLogger(__name__)


class TxTodoPago(models.Model):
    _inherit = 'payment.transaction'

    todopago_RequestKey = fields.Char(
        'RequestKey',
    )
    todopago_PublicRequestKey = fields.Char(
        'PublicRequestKey',
    )
    todopago_Answer = fields.Char(
        'Answer',
    )
    # TODO perhups we can do as we do on mercadopago and send this on
    # the urls with the form_generate_values. But on todopago we still need to
    # ensure we have a transaction before going to todpago to keep the
    # todopago_RequestKey and todopago_PublicRequestKey
    todopago_Return_url = fields.Char(
        'Todopago return url',
    )

    @api.model
    def _todopago_form_get_tx_from_data(self, data):
        Answer = data.get('Answer')
        reference = data.get('OPERATIONID')
        if not reference:
            error_msg = (
                'TodoPago: received data with missing reference (%s) or '
                'OPERATIONID (%s)' % (Answer, reference))
            _logger.error(error_msg)
            raise ValidationError(error_msg)
        transaction = self.search([
            ('reference', '=', reference)], limit=1)

        if not transaction:
            error_msg = (
                'TodoPago: received data for reference %s; no order found' % (
                    reference))
            _logger.error(error_msg)
            raise ValidationError(error_msg)
        transaction.todopago_Answer = Answer
        return transaction

    @api.multi
    def _todopago_form_get_invalid_parameters(self, data):
        invalid_parameters = []
        return invalid_parameters

    @api.multi
    def _todopago_form_validate(self, data):
        """
        """
        tx = self
        _logger.info('Todo pago form validate for tx %s with data %s',
                     tx, data)
        # si no hubo answer en _todopago_form_get_tx_from_data entonces
        # es probable que ni siquiera nos pudimos comunicar con todopago
        if not tx.todopago_Answer or not tx.todopago_RequestKey:
            _logger.info(
                'Received notification for TodoPago payment %s: '
                'set as errored', tx.reference)
            # el mensaje de error ya lo escribimos antes, aca solamente
            # terminamos de stear el estado de error, aunque ya se podria
            # haber hecho todo junto arriba
            return tx.write({
                'state': 'error',
            })
        # we need to get answer form todopago
        answer_data = {
            'Security': str(tx.acquirer_id.todopago_secret_key),
            'Merchant': str(tx.acquirer_id.todopago_client_id),
            'RequestKey': str(tx.todopago_RequestKey),
            'AnswerKey': str(tx.todopago_Answer),
        }
        tpc = tx.acquirer_id.get_TodoPagoConnector()
        AA = tpc.getAuthorizeAnswer(answer_data)
        status = AA.StatusCode

        vals = {
            # 'todopago_RequestKey': str(tx.todopago_RequestKey),
            # 'todopago_Answer': str(tx.todopago_Answer),
            'acquirer_reference': AA.AuthorizationKey,
            'state_message': '%s. %s' % (AA.StatusMessage, AA.Payload),
        }
        if status == -1:
            _logger.info(
                'Validated TodoPago payment for tx %s: set as done',
                tx.reference)
            vals.update(
                state='done',
                # state_message='%s. %s' % (AA.StatusMessage, AA.Payload),
                date_validate=vals.get('payment_date', fields.datetime.now())
            )
            return tx.write(vals)
        else:
            _logger.info(
                'Received notification for TodoPago payment %s: '
                'set as errored', tx.reference)
            vals.update(
                state='error',
                # state='cancel',
                # state_message=AA.StatusMessage
            )
            return tx.write(vals)
