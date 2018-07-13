# pylint: disable-all
# flake8: noqa
class OperationByIdData:

    def get_operation_by_id_params(self):
        return {
            "MERCHANT": "11123",
            "OPERATIONID": "06"
        }

    def get_operation_by_id_worng_params(self):
        return {
            "MERCHANT": "1123",
            "OPERATIONID": "06"
        }

    def get_operation_by_id_params_merchant_null(self):
        return {
            "MERCHANT": "",
            "OPERATIONID": "06"
        }

    def get_operation_by_id_params_operation_null(self):
        return {
            "MERCHANT": "2686",
            "OPERATIONID": ""
        }

    def get_request_ok_response(self):
        return {'OperationsColections': {'Operations': {'COUPONEXPDATE': {'@nil': 'true'}, 'REFUNDED': {'@nil': 'true'}, 'CARDHOLDERNAME': 'prueba', 'CUSTOMEREMAIL': 'prueba@mail.com', 'CREDITEDAMOUNTBUYER': 3.0, 'FEEAMOUNTBUYER': {'@nil': 'true'}, 'IDCONTRACARGO': 0, 'AUTHORIZATIONCODE': 654402, 'COUPONSUBSCRIBER': {'@nil': 'true'}, 'PAYMENTMETHODTYPE': 'Cr\xe9dito', 'AMOUNT': 3.0, 'CARDNUMBER': '45079900XXXXXX0010', 'COUPONSECEXPDATE': {'@nil': 'true'}, 'PAYMENTMETHODNAME': 'VISA', 'RESULTCODE': -1, 'PUSHNOTIFYENDPOINT': {'@nil': 'true'}, 'PAYMENTMETHODCODE': 42, 'TICKETNUMBER': 12, 'REFUNDS': None, 'IDENTIFICATIONTYPE': 'DNI', 'CURRENCYCODE': 32, 'DATETIME': '2017-01-19T17:01:19.553-03:00', 'AMOUNTBUYER': 3.0, 'BANKID': 11, 'COMISION': {'@nil': 'true'}, 'SERVICECHARGEAMOUNT': {'@nil': 'true'}, 'PROMOTIONID': 2708, 'PUSHNOTIFYMETHOD': {'@nil': 'true'}, 'TAXAMOUNT': {'@nil': 'true'}, 'FECHANOTIFICACIONCUENTA': {'@nil': 'true'}, 'BARCODE': {'@nil': 'true'}, 'RESULTMESSAGE': 'APROBADA', 'CREDITEDAMOUNT': 3.0, 'PUSHNOTIFYSTATES': {'@nil': 'true'}, 'ESTADOCONTRACARGO': {'@nil': 'true'}, 'INSTALLMENTPAYMENTS': 3, 'IDENTIFICATION': 32165421, 'TAXAMOUNTBUYER': {'@nil': 'true'}, 'TYPE': 'compra_online', 'FEEAMOUNT': {'@nil': 'true'}, 'OPERATIONID': '06'}}}

    def get_request_fail_response(self):
        return {'OperationsColections': ''}

    def get_request_merchant_null_response(self):
        return {'OperationsColections': {'Status': 1014}}

    def get_request_702_response(self):
        return {'OperationsColections': {'Status': 702}}
