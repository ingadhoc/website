# pylint: disable-all
# flake8: noqa
class DiscoverPaymentMethod:

    def get_request_ok_response(self):
        return {'PaymentMethodCollection': [{'Logo': 'http://10.123.4.121:8092/images/AMEX.png', 'Name': 'AMEX', 'ID': 1}, {'Logo': 'http://10.123.4.121:8092/images/DINERS.png', 'Name': 'DINERS', 'ID': 2}, {'Logo': 'http://10.123.4.121:8092/images/CABAL.png', 'Name': 'CABAL', 'ID': 6}, {'Logo': 'http://10.123.4.121:8092/images/MC.png', 'Name': 'MASTERCARD', 'ID': 14}, {'Logo': 'http://10.123.4.121:8092/images/VISA.png', 'Name': 'VISA', 'ID': 42}, {'Logo': 'http://10.123.4.121:8092/images/VISAD.png', 'Name': 'VISA DEBITO', 'ID': 43}, {'Logo': 'http://10.123.4.121:8092/images/CABALD.png', 'Name': 'CABAL24', 'ID': 129}, {'Logo': 'http://10.123.4.121:8092/images/RAPIPAGO.png', 'Name': 'RAPIPAGO', 'ID': 500}, {'Logo': 'http://10.123.4.121:8092/images/VISAR.jpg', 'Name': 'VISA RECARGABLE', 'ID': 900}, {'Logo': 'http://10.123.4.121:8092/images/MCD.png', 'Name': 'MASTER DEBIT', 'ID': 907}]}
