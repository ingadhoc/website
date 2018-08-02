# pylint: disable-all
# flake8: noqa
class SendAuthorizeRequestData:

    def get_options_SAR_comercio_params(self):
        return {
            'Merchant': "11123",
            "Security": "18ea370805e7471da5ea8c6879b61f22",
            "EncodingMethod": "XML",
            "URL_OK": "http,//someurl.com/ok/",
            "URL_ERROR": "http,//someurl.com/fail/",
            "EMAILCLIENTE": "email_cliente@dominio.com"
        }

    def get_options_SAR_operation_params(self):
        return {
            "MERCHANT": "11123",
            "OPERATIONID": "06",
            "CURRENCYCODE": "032",
            "AMOUNT": "3",
            "MININSTALLMENTS": "3",
            "MAXINSTALLMENTS": "6",
            "CSBTCITY": "Villa General Belgrano",
            "CSSTCITY": "Villa General Belgrano",
            "CSMDD6": "",
            "CSBTCOUNTRY": "AR",
            "CSSTCOUNTRY": "AR",

            "CSBTEMAIL": "todopago@hotmail.com",
            "CSSTEMAIL": "todopago@hotmail.com",

            "CSBTFIRSTNAME": "Juan",
            "CSSTFIRSTNAME": "Juan",

            "CSBTLASTNAME": "Perez",
            "CSSTLASTNAME": "Perez",

            "CSBTPHONENUMBER": "541160913988",
            "CSSTPHONENUMBER": "541160913988",

            "CSBTPOSTALCODE": "1010",
            "CSSTPOSTALCODE": "1010",

            "CSBTSTATE": "B",
            "CSSTSTATE": "B",

            "CSBTSTREET1": "Cerrito 740",
            "CSSTSTREET1": "Cerrito 740",


            "CSBTSTREET2": "Cerrito 740",
            "CSSTSTREET2": "Cerrito 740",

            "CSBTCUSTOMERID": "453458",
            "CSBTIPADDRESS": "192.0.0.4",
            "CSPTCURRENCY": "ARS",
            "CSPTGRANDTOTALAMOUNT": "125.38",
            "CSMDD7": "",
            "CSMDD8": "Y",
            "CSMDD9": "",
            "CSMDD10": "",
            "CSMDD11": "",
            "STCITY": "rosario",
            "STCOUNTRY": "",
            "STEMAIL": "jose@gmail.com",
            "STFIRSTNAME": "Jose",
            "STLASTNAME": "Perez",
            "STPHONENUMBER": "541155893737",
            "STPOSTALCODE": "1414",
            "STSTATE": "D",
            "STSTREET1": "San Martin 123",
            "CSMDD12": "",
            "CSMDD13": "",
            "CSMDD14": "",
            "CSMDD15": "",
            "CSMDD16": "",
            "CSITPRODUCTCODE": "electronic_good",
            "CSITPRODUCTDESCRIPTION": "NOTEBOOK L845 SP4304LA DF TOSHIBA",
            "CSITPRODUCTNAME": "NOTEBOOK L845 SP4304LA DF TOSHIBA",
            "CSITPRODUCTSKU": "LEVJNSL36GN",
            "CSITTOTALAMOUNT": "1254.40",
            "CSITQUANTITY": "1",
            "CSITUNITPRICE": "1254.40"
        }

    def send_authorize_request_ok_response(self):
        return {
            "RequestKey": "20c8abb6-343f-eb40-d524-84b464be0c27",
            "PublicRequestKey": "t48ae3e60-5cb0-9fb1-7608-4cff0c83f24b",
            "URL_Request": "https://developers.todopago.com.ar/formulario/commands?command=formulario&m=t48ae3e60-5cb0-9fb1-7608-4cff0c83f24b",
            "StatusMessage": "Solicitud de Autorizacion Registrada",
            "StatusCode": -1
        }

    def send_authorize_request_fail_response(self):
        return {
            "StatusCode": 98001,
            "StatusMessage": "El campo CSBTCITY es obligatorio."
        }

    def send_authorize_request_702_response(self):
        return {
            "StatusCode": 702,
            "StatusMessage": "Cuanta de Vendedor Invalida"
        }
