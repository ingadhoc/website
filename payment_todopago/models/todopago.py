##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
import logging
import urllib.parse as urlparse
from werkzeug import url_encode
from odoo.addons.payment.models.payment_acquirer import ValidationError
from odoo.addons.payment_todopago.controllers.main import (
    TodoPagoController)
from odoo import api, fields, models, _
import string
from ast import literal_eval
from odoo.http import request
from email.utils import parseaddr
from odoo.addons.payment_todopago.todopago import todopagoconnector as tp
_logger = logging.getLogger(__name__)


# configAuthorization.set('PRISMA f3d8b72c94ab4a06be2ef7c95490f7d3')

class AcquirerMercadopago(models.Model):
    _inherit = 'payment.acquirer'

    @api.model
    def _get_providers(self):
        """
        We add todopago on providers selection field
        """
        providers = super(AcquirerMercadopago, self)._get_providers()
        providers.append(['todopago', 'TodoPago'])
        return providers

    todopago_client_id = fields.Char(
        'TodoPago Merchant Id',
        required_if_provider='todopago',
        help='For eg. 11123',
    )
    todopago_secret_key = fields.Char(
        'TodoPago Secret Key',
        help='For eg. TODOPAGO 4C841713E65FBC7719D666CCAC531234',
        required_if_provider='todopago',
    )

    @api.multi
    def get_TodoPagoConnector(self):
        self.ensure_one()
        j_header_http = {"Authorization": self.todopago_secret_key}
        return tp.TodoPagoConnector(j_header_http, self.environment)

    @api.multi
    def todopago_compute_fees(self, amount, currency_id, country_id):
        """ We add [provider]_compute_fees method
            Compute todopago fees.

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
    def todopago_form_generate_values(self, values):
        """
        Por ahora stamos haciendo que si no vienen datos se usen datos del
        commercial partner, pero esto seguro lo podriamos mejorar
        """
        # return {}, tx_values
        # return values, tx_values
        self.ensure_one()
        tx_values = dict(values)
        if (
                not self.todopago_client_id or
                not self.todopago_secret_key
        ):
            raise ValidationError(_(
                'YOU MUST COMPLETE acquirer.todopago_client_id and '
                'acquirer.todopago_secret_key'))

        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        success_url = TodoPagoController._success_url
        failure_url = TodoPagoController._failure_url
        commercial_partner = tx_values['partner'].commercial_partner_id

        # get some values and catch errors
        errors = []
        # mandatorio, ya es mandatorio en ecommerce. Ademas parece ser solo
        # para argentina ya que requiere provincia en codigos argentinos
        country = (
            values['billing_partner_country'] and values[
                'billing_partner_country'].code or
            'AR').encode("utf8")
        if country != 'AR':
            errors.append('Only Argentina Implemented for TODOPAGO')

        # mandatorio y exije que moneda sea ars segun
        # https://github.com/TodoPago/SDK-Python#generalidades
        currency = (tx_values['currency'] and tx_values['currency'].name or '')
        if currency != 'ARS':
            errors.append('Only ARS Currency Implemented for TODOPAGO')

        # usamos estado generico de bs as si no viene definido
        if values['billing_partner_state'] and values[
                'billing_partner_state'].code:
            state = values['billing_partner_state'].code
        else:
            state = 'B'

        # TODOPAGO necesita que el codigo de provincia sea alguno de estos
        todopago_state_codes = [
            'C', 'B', 'K', 'H', 'U', 'X', 'W', 'E', 'P', 'Y', 'L', 'F', 'M',
            'N', 'Q', 'R', 'A', 'J', 'D', 'Z', 'S', 'G', 'V', 'T']
        if state not in todopago_state_codes:
            state = 'B'
        state = state.encode("utf8")

        if errors:
            # if errors, then we dont send todopago_data and button is not
            # display
            _logger.info('Todo pago method not avialble because of %s' % (
                errors))
            return tx_values

        # clean phone, only numbers
        # con esto obtenemos listas de reemplazo para lo que queremos limpiar
        string_all = string.maketrans('', '')
        onlydigits = string_all.translate(string_all, string.digits)
        onlyletters = string_all.translate(string_all, string.letters + ' ')
        letters_digits = string_all.translate(
            string_all, string.letters + string.digits + ' ')

        phone = values["billing_partner_phone"]
        phone = phone or commercial_partner.phone
        phone = str(phone).translate(string_all, onlydigits) or "12345678"
        # todopago no nos acepta mas de 13 caraceteres
        phone = phone[:13]

        amount = "%.2f" % round(tx_values['amount'], 2)

        # parse emil address
        email = parseaddr(values["partner_email"])[1]
        email = email or commercial_partner.email
        if not email or '@' not in email:
            email = 'dummy@email.com'
        email = email.strip().encode("utf8")
        # no acepta mas de 100
        email = email[:100]

        # mandatorio, ya es mandatorio en ecommerce
        city = values["billing_partner_city"]
        city = city or commercial_partner.city or 'DUMMY CITY'
        city = city.encode("utf8").translate(string_all, letters_digits)
        # no acepta mas de 50
        city = city[:50]

        street = values["billing_partner_address"]
        street = street or commercial_partner.street or 'DUMMY STREET'
        street = street.encode("utf8").translate(string_all, letters_digits)
        # no acepta mas de 60
        street = street[:60]

        postal_code = values["billing_partner_zip"]
        postal_code = (postal_code or commercial_partner.zip or '1000')
        postal_code = postal_code.encode("utf8").translate(
            string_all, letters_digits)
        # no acepta mas de 10
        postal_code = postal_code[:10]

        first_name = values["billing_partner_first_name"]
        last_name = values["billing_partner_last_name"]
        # todopago only accept lettters
        first_name = str(first_name.encode("utf8")).translate(
            string_all, onlyletters)
        last_name = str(last_name.encode("utf8")).translate(
            string_all, onlyletters)
        # no acepta mas de 60
        first_name = first_name[:10]
        last_name = last_name[:10]

        # TODO tal vez necesitariamos separar primer y segundo nombre
        # en el caso que solo haya una palabra
        if not first_name:
            first_name = last_name
        OPERATIONID = str(tx_values["reference"])
        # cargamos todos los datos obligatorios: facturacion (CSB), envio (CSS)
        # y de los prioductos
        # we use str o encode because not unicode supported
        optionsSAR_operacion = {
            "MERCHANT": str(self.todopago_client_id),
            "EMAILCLIENTE": email,
            "OPERATIONID": OPERATIONID,
            "CURRENCYCODE": str("032"),
            "AMOUNT": str(tx_values["amount"]),
            "CSBTCITY": city,
            "CSSTCITY": city,
            "CSBTCOUNTRY": country,
            "CSSTCOUNTRY": country,
            "CSBTIPADDRESS": request.httprequest.remote_addr,
            # id al que se le genera la factura
            "CSBTCUSTOMERID": str(commercial_partner.id),
            # email is mandatory for us too
            "CSBTEMAIL": email,
            "CSSTEMAIL": email,
            "CSBTSTREET1": street,
            "CSSTSTREET1": street,
            "CSBTPOSTALCODE": postal_code,
            "CSSTPOSTALCODE": postal_code,
            "CSBTFIRSTNAME": first_name,
            "CSSTFIRSTNAME": first_name,
            "CSBTLASTNAME": last_name,
            "CSSTLASTNAME": last_name,
            "CSBTPHONENUMBER": phone,
            "CSSTPHONENUMBER": phone,
            "CSBTSTATE": state,
            "CSSTSTATE": state,
            "CSPTGRANDTOTALAMOUNT": amount,
            "CSPTCURRENCY": "ARS",
            # otros del producto
            'CSITPRODUCTCODE': "generic_product",
            'CSITPRODUCTDESCRIPTION': "Generic Description",
            'CSITPRODUCTNAME': "GenericProduct",
            'CSITPRODUCTSKU': "GENPROD",
            'CSITTOTALAMOUNT': amount,
            'CSITQUANTITY': "1",
            'CSITUNITPRICE': amount,
        }

        # agregamos cargos si está activo
        if self.fees_active:
            fee_amount = "%.2f" % round(tx_values.get('fees', 0.0), 2)
            total_amount = "%.2f" % round(
                tx_values['amount'] + tx_values.pop('fees', 0.0), 2)
            optionsSAR_operacion.update({
                'CSITPRODUCTCODE': "generic_product#recargo",
                'CSITPRODUCTDESCRIPTION': (
                    "Generic Description#Recargo por uso Todopago"),
                'CSITPRODUCTNAME': "GenericProduct#Recargo",
                'CSITPRODUCTSKU': "GENPROD#RECARGO",
                'CSITTOTALAMOUNT': '%s#%s' % (amount, fee_amount),
                'CSITQUANTITY': "1#1",
                'CSITUNITPRICE': '%s#%s' % (amount, fee_amount),
                'CSPTGRANDTOTALAMOUNT': total_amount,
                'AMOUNT': total_amount,
            })

        URL_ERROR = "%s?%s" % (
            urlparse.urljoin(base_url, failure_url),
            url_encode({'OPERATIONID': OPERATIONID}))
        URL_OK = "%s?%s" % (
            urlparse.urljoin(base_url, success_url),
            url_encode({'OPERATIONID': OPERATIONID}))
        optionsSAR_comercio = {
            # "Session": "ABCDEF-1234-12221-FDE1-00000200",
            "Security": str(self.todopago_secret_key),
            "EncodingMethod": "XML",
            "URL_OK": str(URL_OK),
            "URL_ERROR": str(URL_ERROR),
            # "EMAILCLIENTE": email,
            "Merchant":  str(self.todopago_client_id),
        }

        tx_values.update({
            'todopago_data': {
                'optionsSAR_operacion': optionsSAR_operacion,
                'optionsSAR_comercio': optionsSAR_comercio,
                'todopago_client_id': self.todopago_client_id,
                'todopago_secret_key': self.todopago_secret_key,
                # 'environment': self.environment,
                'acquirer_id': self.id,
                'partner_id': commercial_partner.id,
                'amount': tx_values['amount'],
                'currency_id': tx_values['currency'].id,
                'return_url': tx_values['return_url'],
            }
        })
        return tx_values

    @api.multi
    def todopago_get_form_action_url(self):
        self.ensure_one()
        """
        Este metodo se llama cada vez que se ve el boton asi que no
        lo podemos usar para mucho
        """
        return TodoPagoController._create_preference_url

    @api.multi
    def _todopago_create_transaction(self, data):
        # TODO en realidad podriamos consturir toda la data aca y no en
        # todopago_form_generate_values
        self.ensure_one()
        _logger.info('Creating transaction on todopago')
        todopago_data = literal_eval(data.get('todopago_data', {}))
        partner_id = todopago_data.get('partner_id')
        amount = todopago_data.get('amount')
        currency_id = todopago_data.get('currency_id')
        optionsSAR_comercio = todopago_data.get(
            'optionsSAR_comercio')
        optionsSAR_operacion = todopago_data.get(
            'optionsSAR_operacion')
        return_url = todopago_data.get(
            'return_url')

        transactions = self.env['payment.transaction'].search([
            ('reference', '=', optionsSAR_operacion['OPERATIONID'])])

        # la unica manera que vimos de sacar un campo de la sale order es acá
        sale = transactions and transactions[0].sale_order_id
        if sale.todopago_max_insallments:
            optionsSAR_operacion['MAXINSTALLMENTS'] = \
                str(sale.todopago_max_insallments)

        tpc = self.get_TodoPagoConnector()
        _logger.info('Sending sendAuthorizeRequest')
        response = tpc.sendAuthorizeRequest(
            optionsSAR_comercio, optionsSAR_operacion)
        _logger.info('Preference Result: %s' % response)

        # TODO tal vez deberiamos agregar un try por si el error no esta
        # atrapado y obtenemos una respuesta no contemplada
        if response.StatusCode != -1:
            _logger.error('Error: StatusCode "%s", StatusMessage "%s"' % (
                response.StatusCode, response.StatusMessage))
            # escribimos la return url en la transaccion, ya que es usada
            # luego de procesar el error, seguramente seria mejor en otro lado
            transactions.write({
                'todopago_Return_url': return_url,
                'state_message': 'Error %s: %s' % (
                    response.StatusCode, response.StatusMessage),
            })
            # si tenemos una url de error disponible, la devolvemos
            # esto pasa por ej cuando no esta todopago configurado
            # return "/"
            return optionsSAR_comercio.get('URL_ERROR', "/")
        tr_vals = {
            'todopago_RequestKey': response.RequestKey,
            'todopago_PublicRequestKey': response.PublicRequestKey,
            'todopago_Return_url': return_url,
        }
        # desde el website la transaccion ya esta creadas, desde SO no, por
        # eso lo hacemos asi
        for transaction in transactions:
            if transaction.state not in ['cancel', 'error']:
                _logger.info('Writing transaction id %s with data %s' % (
                    transaction.id, tr_vals))
                transaction.write(tr_vals)
                return response.URL_Request
            # if transaction canceled, we replace number to aboid constrain
            # error
            # esto no pasa desde el website pero si nos pasa desde ov
            # desde website odoo las renombra correctamente, igual deberiamos
            # verificar que no este corregido en OV
            transaction.reference = "%s-%s" % (
                transaction.reference, transaction.id)
        _logger.info('Creating transaction with data %s' % tr_vals)
        tr_vals.update({
            'partner_id': partner_id,
            'acquirer_id': self.id,
            'currency_id': currency_id,
            'acquirer_reference': 'todopago',
            'reference': optionsSAR_operacion['OPERATIONID'],
            'amount': amount,
        })
        # en realidad creo que no lo deberiamos crear aca nosotros, es la ruta
        # shop/payment/transaction que lo crea
        transaction = transactions.create(tr_vals)
        return response.URL_Request


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
                'collection_id (%s)' % (Answer, reference))
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

    @api.model
    def _todopago_form_get_invalid_parameters(self, tx, data):
        invalid_parameters = []
        return invalid_parameters

    @api.model
    def _todopago_form_validate(self, tx, data):
        """
        """
        _logger.info('Todo pago form validate for tx %s with data %s' % (
            tx, data))
        # si no hubo answer en _todopago_form_get_tx_from_data entonces
        # es probable que ni siquiera nos pudimos comunicar con todopago
        if not tx.todopago_Answer or not tx.todopago_RequestKey:
            _logger.info(
                'Received notification for TodoPago payment %s: '
                'set as errored' % (tx.reference))
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
                'Validated TodoPago payment for tx %s: set as done' % (
                    tx.reference))
            vals.update(
                state='done',
                # state_message='%s. %s' % (AA.StatusMessage, AA.Payload),
                date_validate=vals.get('payment_date', fields.datetime.now())
            )
            return tx.write(vals)
        else:
            _logger.info(
                'Received notification for TodoPago payment %s: '
                'set as errored' % (tx.reference))
            vals.update(
                state='error',
                # state='cancel',
                # state_message=AA.StatusMessage
            )
            return tx.write(vals)
