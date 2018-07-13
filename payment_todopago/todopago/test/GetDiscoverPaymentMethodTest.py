# pylint: disable-all
# flake8: noqa
import sys
sys.path.append("..")
from todopagoconnector import TodoPagoConnector
from DiscoverPaymentMethodData import DiscoverPaymentMethod
import unittest
from unittest import TestCase
if sys.version_info[0] >= 3:
    from unittest.mock import patch, Mock
else:
    from mock import patch, Mock, MagicMock


class GetDiscoverPaymentMethod(TestCase):

    @patch('todopagoconnector.TodoPagoConnector')
    def test_get_dsicover_ok(self, MockTodoPagoConnector):
        j_header_http = {
            'Authorization': 'TODOPAGO 18ea370805e7471da5ea8c6879b61f22'
        }

        MTPConnector = MockTodoPagoConnector(j_header_http, "test")

        instanceGetDiscoverPM = DiscoverPaymentMethod()

        MTPConnector.discoverPaymentMethods.return_value = instanceGetDiscoverPM.get_request_ok_response()

        responseDiscover = MTPConnector.discoverPaymentMethods()

        self.assertTrue(len(responseDiscover['PaymentMethodCollection']))

    @patch('todopagoconnector.TodoPagoConnector')
    def test_get_discover_fail_conection(self, MockTodoPagoConnector):
        j_header_http = {
            'Authorization': 'TODOPAGO f3d8b72c94ab4a06be2ef7c95490f7d3'
        }

        MTPConnector = MockTodoPagoConnector(j_header_http, "test")

        instanceGetDiscoverPM = DiscoverPaymentMethod()

        MTPConnector.discoverPaymentMethods.return_value = ""

        responseDiscover = MTPConnector.discoverPaymentMethods()

        self.assertFalse(len(responseDiscover))

if __name__ == '__main__':
    unittest.main()
