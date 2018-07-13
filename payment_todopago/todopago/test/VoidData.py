# pylint: disable-all
# flake8: noqa
class VoidData:

    def get_refund_params(self):
        return {
            "Merchant": "2669",
            "Security": "108fc2b7c8a640f2bdd3ed505817ffde",
            "RequestKey": "0d801e1c-e6b1-672c-b717-5ddbe5ab97d6"
        }

    def get_void_request_ok_response(self):
        return {
            "StatusCode": 2011,
            "StatusMessage": "Devolucion OK",
            "AuthorizationKey": "a61de00b-c118-2688-77b0-16dbe5799913",
            "AUTHORIZATIONCODE": 654402
        }

    def get_void_request_fail_response(self):
        return {
            "StatusCode": 2013,
            "StatusMessage": "No es posible obtener los importes de las comisiones para realizar la devolucion",
            "AuthorizationKey": "",
            "AUTHORIZATIONCODE": ""
        }

    def get_void_request_702_response(self):
        return {
            "StatusCode": 702,
            "StatusMessage": "Cuenta de Vendedor Invalida",
            "AuthorizationKey": "",
            "AUTHORIZATIONCODE": ""
        }
