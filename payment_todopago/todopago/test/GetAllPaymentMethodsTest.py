# pylint: disable-all
# flake8: noqa
import sys
sys.path.append("..")
from todopagoconnector import TodoPagoConnector
from GetPaymentMethosData import GetAllPaymentData
import unittest
from unittest import TestCase
if sys.version_info[0] >= 3:
    from unittest.mock import patch, Mock
else:
    from mock import patch, Mock, MagicMock


class GetAllPaymentMethod(TestCase):

    @patch('todopagoconnector.TodoPagoConnector')
    def test_get_credentials_ok(self, MockTodoPagoConnector):
        j_header_http = {
            'Authorization': 'TODOPAGO 18ea370805e7471da5ea8c6879b61f22'
        }

        MTPConnector = MockTodoPagoConnector(j_header_http, "test")

        instancesGetallPM = GetAllPaymentData()

        MTPConnector.getAllPaymentMethods.return_value = instancesGetallPM.get_request_ok_response()

        responseGetAllPaymentMethos = MTPConnector.getAllPaymentMethods(
            instancesGetallPM.get_all_payment_method_params())

        self.assertTrue(len(responseGetAllPaymentMethos['Result']))

    @patch('todopagoconnector.TodoPagoConnector')
    def test_get_credentials_fail_conection(self, MockTodoPagoConnector):
        j_header_http = {
            'Authorization': 'TODOPAGO 18ea370805e7471da5ea8c6879b61f22'
        }

        MTPConnector = MockTodoPagoConnector(j_header_http, "test")

        instancesGetallPM = GetAllPaymentData()

        MTPConnector.getAllPaymentMethods.return_value = ""

        responseGetAllPaymentMethos = MTPConnector.getAllPaymentMethods(
            instancesGetallPM.get_all_payment_method_params())

        self.assertFalse(len(responseGetAllPaymentMethos))

if __name__ == '__main__':
    unittest.main()
