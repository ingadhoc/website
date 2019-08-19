##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
import logging
import string

from urllib.parse import urljoin
from werkzeug import urls
from email.utils import parseaddr

from odoo import api, fields, models, _
from odoo.http import request
from odoo.tools.safe_eval import safe_eval
from odoo.addons.payment.models.payment_acquirer import ValidationError
from ..todopago import todopagoconnector as tp
from ..controllers.main import TodoPagoController

_logger = logging.getLogger(__name__)


class AcquirerTodopago(models.Model):
    _inherit = 'payment.acquirer'

    provider = fields.Selection(selection_add=[('todopago', 'TodoPago')])
    todopago_client_id = fields.Char(
        'TodoPago Prod. Merchant Id',
        required_if_provider='todopago',
        help='For eg. 11123',
    )
    todopago_secret_key = fields.Char(
        'TodoPago Prod. Secret Key',
        help='For eg. TODOPAGO 4C841713E65FBC7719D666CCAC531234',
        required_if_provider='todopago',
    )
    todopago_test_client_id = fields.Char(
        'TodoPago Test Merchant Id',
        help='For eg. 11123',
        required_if_provider='todopago',
    )
    todopago_test_secret_key = fields.Char(
        'TodoPago Test Secret Key',
        required_if_provider='todopago',
    )
    # Default paypal fees
    fees_dom_fixed = fields.Float(default=0)
    fees_dom_var = fields.Float(default=10)
    fees_int_fixed = fields.Float(default=0)
    fees_int_var = fields.Float(default=10)

    @api.multi
    def get_TodoPagoConnector(self):
        self.ensure_one()
        todopago_secret_key = self.todopago_secret_key \
            if self.environment == 'prod' else self.todopago_test_secret_key
        j_header_http = {"Authorization": todopago_secret_key}
        return tp.TodoPagoConnector(j_header_http, self.environment)

    def _get_feature_support(self):
        res = super(AcquirerTodopago, self)._get_feature_support()
        res['fees'].append('todopago')
        return res

    @api.multi
    def todopago_compute_fees(self, amount, currency_id, country_id):
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
        fees = percentage / 100.0 * amount + fixed
        return fees

    @api.multi
    def todopago_form_generate_values(self, values):
        """
        Por ahora stamos haciendo que si no vienen datos se usen datos del
        commercial partner, pero esto seguro lo podriamos mejorar
        """
        # return {}, tx_values
        # return values, tx_values
        todopago_client_id = self.todopago_client_id \
            if self.environment == 'prod' else self.todopago_test_client_id
        todopago_secret_key = self.todopago_secret_key \
            if self.environment == 'prod' else self.todopago_test_secret_key
        self.ensure_one()
        tx_values = dict(values)
        if (
                not todopago_client_id or
                not todopago_secret_key
        ):
            raise ValidationError(_(
                'YOU MUST COMPLETE acquirer.todopago_client_id and '
                'acquirer.todopago_secret_key'))

        base_url = self.env['ir.config_parameter'].sudo().get_param(
            'web.base.url')
        success_url = TodoPagoController._success_url
        failure_url = TodoPagoController._failure_url
        commercial_partner = tx_values['partner'].commercial_partner_id

        # get some values and catch errors
        errors = []
        # mandatorio, ya es mandatorio en ecommerce. Ademas parece ser solo
        # para argentina ya que requiere provincia en codigos argentinos
        country = (
            values['billing_partner_country'] and values[
                'billing_partner_country'].code or 'AR')
        # si bien seria obligatorio que sea argentina, como el error
        # no lo tenemos bien atrapado, probamos seguir adelante
        # if country != 'AR':
        #     errors.append('Only Argentina Implemented for TODOPAGO')

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
            _logger.error(
                'Todo pago method not avialble because of %s', errors)
            return tx_values

        # clean phone, only numbers
        # con esto obtenemos listas de reemplazo para lo que queremos limpiar
        string_all = bytes.maketrans(b'', b'')
        digits = (string.digits).encode()
        letters = (string.ascii_letters + ' ').encode()

        onlydigits = string_all.translate(string_all, digits)
        onlyletters = string_all.translate(string_all, letters)
        letters_digits = string_all.translate(string_all, letters + digits)

        phone = values["billing_partner_phone"]
        phone = (phone or commercial_partner.phone)
        phone = phone if phone else "12345678"
        phone = phone.encode()
        phone = phone.translate(string_all, onlydigits)
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
        first_name = first_name.encode().translate(
            string_all, onlyletters)
        last_name = last_name.encode().translate(
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
            "MERCHANT": str(todopago_client_id),
            # "EMAILCLIENTE": email,
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
            urljoin(base_url, failure_url),
            urls.url_encode({'OPERATIONID': OPERATIONID}))
        URL_OK = "%s?%s" % (
            urljoin(base_url, success_url),
            urls.url_encode({'OPERATIONID': OPERATIONID}))
        optionsSAR_comercio = {
            # "Session": "ABCDEF-1234-12221-FDE1-00000200",
            "Security": str(todopago_secret_key),
            "EncodingMethod": "XML",
            "URL_OK": str(URL_OK),
            "URL_ERROR": str(URL_ERROR),
            # "EMAILCLIENTE": email,
            "Merchant":  str(todopago_client_id),
        }

        tx_values.update({
            'todopago_data': {
                'optionsSAR_operacion': optionsSAR_operacion,
                'optionsSAR_comercio': optionsSAR_comercio,
                'todopago_client_id': todopago_client_id,
                'todopago_secret_key': todopago_secret_key,
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
        """
        Este metodo se llama cada vez que se ve el boton asi que no
        lo podemos usar para mucho
        """
        self.ensure_one()
        return TodoPagoController._create_preference_url

    @api.multi
    def _todopago_create_transaction(self, data):
        # TODO en realidad podriamos consturir toda la data aca y no en
        # todopago_form_generate_values
        self.ensure_one()
        _logger.info('Creating transaction on todopago')
        todopago_data = safe_eval(data.get('todopago_data', {}))
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
        sales = transactions.mapped('sale_order_ids')
        if sales and sales[0].todopago_max_installments:
            optionsSAR_operacion['MAXINSTALLMENTS'] = \
                str(sales[0].todopago_max_installments)

        tpc = self.get_TodoPagoConnector()
        _logger.info('Sending sendAuthorizeRequest')

        for (key, value) in optionsSAR_operacion.items():
            if isinstance(value, bytes):
                optionsSAR_operacion[key] = value.decode()

        response = tpc.sendAuthorizeRequest(
            optionsSAR_comercio, optionsSAR_operacion)
        _logger.log(25, 'Preference Result: %s', response)

        # TODO tal vez deberiamos agregar un try por si el error no esta
        # atrapado y obtenemos una respuesta no contemplada
        if response.StatusCode != -1:
            _logger.error('Error: StatusCode "%s", StatusMessage "%s"',
                          response.StatusCode, response.StatusMessage)
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
                _logger.info('Writing transaction id %s with data %s',
                             transaction.id, tr_vals)
                transaction.write(tr_vals)
                return response.URL_Request
            # if transaction canceled, we replace number to aboid constrain
            # error
            # esto no pasa desde el website pero si nos pasa desde ov
            # desde website odoo las renombra correctamente, igual deberiamos
            # verificar que no este corregido en OV
            transaction.reference = "%s-%s" % (
                transaction.reference, transaction.id)
        _logger.info('Creating transaction with data %s', tr_vals)
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
