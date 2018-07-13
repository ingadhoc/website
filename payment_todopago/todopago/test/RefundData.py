# pylint: disable-all
# flake8: noqa
class RefundsData:

    def get_refund_params(self):
        return {
            "Merchant": "2153",
            "Security": "f3d8b72c94ab4a06be2ef7c95490f7d3",
            "RequestKey": "a2fc7d9e-7c7d-8a55-5322-cecb593160d3",
            "AMOUNT": "1.00"
        }

    def get_request_ok_response(self):
        return {
            "StatusCode": 2011,
            "StatusMessage": "Devolucion OK",
            "AuthorizationKey": "a61de00b-c118-2688-77b0-16dbe5799913",
            "AUTHORIZATIONCODE": 654402
        }

    def get_request_fail_response(self):
        return {
            "StatusCode": 2013,
            "StatusMessage": "No es posible obtener los importes de las comisiones para realizar la devolucion",
            "AuthorizationKey": "",
            "AUTHORIZATIONCODE": ""
        }

    def get_request_702_response(self):
        return {
            "StatusCode": 702,
            "StatusMessage": "Cuenta de Vendedor Invalida",
            "AuthorizationKey": "",
            "AUTHORIZATIONCODE": ""
        }
