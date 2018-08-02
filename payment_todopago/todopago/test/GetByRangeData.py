# pylint: disable-all
# flake8: noqa
class GetByRangeDateTime:

    def get_by_range_method_params(self):
        return {
            "MERCHANT": "11406",
            "STARTDATE": "2016-01-01",
            "ENDDATE": "2017-05-14",
            "PAGENUMBER": "1"
        }

    def get_request_ok_response(self):
        return {'OperationsColections': {'Operations': {'COUPONEXPDATE': {'@nil': 'true'}, 'REFUNDED': {'@nil': 'true'}, 'CARDHOLDERNAME': 'prueba', 'CUSTOMEREMAIL': 'prueba@mail.com', 'CREDITEDAMOUNTBUYER': 3.0, 'FEEAMOUNTBUYER': {'@nil': 'true'}, 'IDCONTRACARGO': 0, 'AUTHORIZATIONCODE': 654402, 'COUPONSUBSCRIBER': {'@nil': 'true'}, 'PAYMENTMETHODTYPE': 'Cr\xe9dito', 'AMOUNT': 3.0, 'CARDNUMBER': '45079900XXXXXX0010', 'COUPONSECEXPDATE': {'@nil': 'true'}, 'PAYMENTMETHODNAME': 'VISA', 'RESULTCODE': -1, 'PUSHNOTIFYENDPOINT': {'@nil': 'true'}, 'PAYMENTMETHODCODE': 42, 'TICKETNUMBER': 12, 'REFUNDS': None, 'IDENTIFICATIONTYPE': 'DNI', 'CURRENCYCODE': 32, 'DATETIME': '2017-01-19T17:01:19.553-03:00', 'AMOUNTBUYER': 3.0, 'BANKID': 11, 'COMISION': {'@nil': 'true'}, 'SERVICECHARGEAMOUNT': {'@nil': 'true'}, 'PROMOTIONID': 2708, 'PUSHNOTIFYMETHOD': {'@nil': 'true'}, 'TAXAMOUNT': {'@nil': 'true'}, 'FECHANOTIFICACIONCUENTA': {'@nil': 'true'}, 'BARCODE': {'@nil': 'true'}, 'RESULTMESSAGE': 'APROBADA', 'CREDITEDAMOUNT': 3.0, 'PUSHNOTIFYSTATES': {'@nil': 'true'}, 'ESTADOCONTRACARGO': {'@nil': 'true'}, 'INSTALLMENTPAYMENTS': 3, 'IDENTIFICATION': 32165421, 'TAXAMOUNTBUYER': {'@nil': 'true'}, 'TYPE': 'compra_online', 'FEEAMOUNT': {'@nil': 'true'}, 'OPERATIONID': '06'}}}
