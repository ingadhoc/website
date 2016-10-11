# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
import logging
import urlparse
from openerp.exceptions import Warning
from openerp.addons.payment.models.payment_acquirer import ValidationError
from openerp.addons.payment_mercadopago.controllers.main import (
    MercadoPagoController)
from openerp import api, fields, models, _

_logger = logging.getLogger(__name__)


class AcquirerMercadopago(models.Model):
    _inherit = 'payment.acquirer'

    @api.model
    def _get_providers(self):
        """
        We add mercadopago on providers selection field
        """
        providers = super(AcquirerMercadopago,
                          self)._get_providers()
        providers.append(['mercadopago', 'MercadoPago'])
        return providers

    # mercadopago_item_type = fields.Selection([
    #     ('so_lines', 'Send SO lines detail'),
    #     ('generic_message', 'Generic Message'),
    #     ],
    #     'Mercadopago Description',
    #     )
    mercadopago_item_title = fields.Char(
        'MercadoPago Item Title',
        help='Yo need to use %s to indicate '
             'where SO number must go',
        default='Orden Ecommerce %s',
        )
    mercadopago_client_id = fields.Char(
        'MercadoPago Client Id',
        required_if_provider='mercadopago',
        )
    mercadopago_secret_key = fields.Char(
        'MercadoPago Secret Key',
        required_if_provider='mercadopago',
        )

    @api.multi
    def mercadopago_compute_fees(
            self, amount, currency_id, country_id):
        """ We add [provider]_compute_fees method
            Compute mercadopago fees.

            :param float amount: the amount to pay
            :param integer country_id:
            an ID of a res.country, or None.
            This is the customer's country, to be
            compared to the acquirer company country.
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
        fees = \
            (percentage / 100.0 * amount + fixed) / (1 - percentage / 100.0)
        return fees

    @api.multi
    def mercadopago_form_generate_values(self, partner_values, tx_values):
        self.ensure_one()
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        if (
                not self.mercadopago_client_id or
                not self.mercadopago_secret_key
                ):
            raise ValidationError(_(
                'YOU MUST COMPLETE acquirer.mercadopago_client_id and '
                'acquirer.mercadopago_secret_key'))
        if tx_values.get('return_url'):
            success_url = MercadoPagoController._success_url
            failure_url = MercadoPagoController._failure_url
            pending_url = MercadoPagoController._pending_url
        else:
            success_url = MercadoPagoController._success_no_return_url
            failure_url = MercadoPagoController._pending_no_return_url
            pending_url = MercadoPagoController._pending_url

        # TODO, implement, not implemented yet because mercadopago only
        # shows description of first line and we would need to send taxes too
        # sale_order = self.env['sale.order'].search(
        #     [('name', '=', tx_values["reference"])], limit=1)
        # if self.mercadopago_description == 'so_lines' and sale_order:
        #     items = [{
        #         "title": line.name,
        #         "quantity": line.product_uom_qty,
        #         "currency_id": (
        #             tx_values['currency'] and
        #             tx_values['currency'].name or ''),
        #         "unit_price": line.price_unit,
        #     } for line in sale_order.order_line]
        # else:
        if (
                not self.mercadopago_item_title or
                "%s" not in self.mercadopago_item_title
                ):
            raise Warning(_(
                'No generic message defined for mercadopago or message '
                'does not contains %/s!'))
        items = [{
            "title": self.mercadopago_item_title % (
                tx_values["reference"]),
            # "title": _("Orden Ecommerce %s") % tx_values["reference"],
            "quantity": 1,
            "currency_id": (
                tx_values['currency'] and
                tx_values['currency'].name or ''),
            "unit_price": tx_values["amount"],
        }]

        preference = {
            "items": items,
            "payer": {
                "name": partner_values["first_name"],
                "surname": partner_values["last_name"],
                "email": partner_values["email"],
                },
            "back_urls": {
                "success": '%s' % urlparse.urljoin(
                    base_url, success_url),
                "failure": '%s' % urlparse.urljoin(
                    base_url, failure_url),
                "pending": '%s' % urlparse.urljoin(
                    base_url, pending_url)
                },
            # "notification_url": '%s' % urlparse.urljoin(
            #     base_url, MercadoPagoController._notify_url),
            "auto_return": "approved",
            "external_reference": tx_values["reference"],
            "expires": False,
            }
        tx_values['mercadopago_data'] = {
            'mercadopago_preference': preference,
            'mercadopago_client_id': self.mercadopago_client_id,
            'mercadopago_secret_key': self.mercadopago_secret_key,
            'environment': self.environment,
            }
        return partner_values, tx_values

    @api.multi
    def mercadopago_get_form_action_url(self):
        self.ensure_one()
        return MercadoPagoController._create_preference_url


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
        # TODO implementar invalid paramters desde
        # https://www.mercadopago.com.ar/developers/es/api-docs/
        # basic-checkout/checkout-preferences/
        # if data.get('pspReference'):
        # _logger.warning('Received a notification from MercadoLibre.')
        return invalid_parameters

    @api.model
    def _mercadopago_form_validate(self, tx, data):
        """
        From:
        https://developers.mercadopago.com/documentacion/notificaciones-de-pago
        Por lo que vi nunca se devuelve la "cancel_reason" o "pending_reason"
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
