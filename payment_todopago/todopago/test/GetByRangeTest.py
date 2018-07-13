# pylint: disable-all
# flake8: noqa
import sys
sys.path.append("..")
from todopagoconnector import TodoPagoConnector
from GetByRangeData import GetByRangeDateTime
import unittest
from unittest import TestCase
if sys.version_info[0] >= 3:
    from unittest.mock import patch, Mock
else:
    from mock import patch, Mock, MagicMock


class GetByRangeMethod(TestCase):

    @patch('todopagoconnector.TodoPagoConnector')
    def test_get_credentials_ok(self, MockTodoPagoConnector):
        j_header_http = {
            'Authorization': 'TODOPAGO 18ea370805e7471da5ea8c6879b61f22'
        }

        MTPConnector = MockTodoPagoConnector(j_header_http, "test")

        instancesGetByRange = GetByRangeDateTime()

        MTPConnector.getAllPaymentMethods.return_value = instancesGetByRange.get_request_ok_response()

        responseGetByRange = MTPConnector.getAllPaymentMethods(
            instancesGetByRange.get_by_range_method_params())

        self.assertTrue(len(responseGetByRange))

    @patch('todopagoconnector.TodoPagoConnector')
    def test_get_credentials_fail_conection(self, MockTodoPagoConnector):
        j_header_http = {
            'Authorization': 'TODOPAGO 18ea370805e7471da5ea8c6879b61f22'
        }

        MTPConnector = MockTodoPagoConnector(j_header_http, "test")

        instancesGetByRange = GetByRangeDateTime()

        MTPConnector.getByRangeDateTime.return_value = ""

        responseGetByRange = MTPConnector.getByRangeDateTime(
            instancesGetByRange.get_by_range_method_params())

        self.assertFalse(len(responseGetByRange))

if __name__ == '__main__':
    unittest.main()
