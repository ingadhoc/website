# pylint: disable-all
# flake8: noqa
import sys
sys.path.append("..")
from todopagoconnector import TodoPagoConnector
from VoidData import VoidData
import unittest
from unittest import TestCase
if sys.version_info[0] >= 3:
    from unittest.mock import patch, Mock
else:
    from mock import patch, Mock, MagicMock


class GetRefundTest(TestCase):
    @patch('todopagoconnector.TodoPagoConnector')
    def test_get_void_ok(self, MockTodoPagoConnector):
        j_header_http = {
            'Authorization': 'TODOPAGO f3d8b72c94ab4a06be2ef7c95490f7d3'
        }

        MTPConnector = MockTodoPagoConnector(j_header_http, "test")

        instanceVoidData = VoidData()

        MTPConnector.voidRequest.return_value = instanceVoidData.get_void_request_ok_response()

        responseRefund = MTPConnector.voidRequest(
            instanceVoidData.get_refund_params)

        self.assertEquals(responseRefund['StatusCode'], 2011)

    @patch('todopagoconnector.TodoPagoConnector')
    def test_get_void_fail(self, MockTodoPagoConnector):
        j_header_http = {
            'Authorization': 'TODOPAGO f3d8b72c94ab4a06be2ef7c95490f7d3'
        }

        MTPConnector = MockTodoPagoConnector(j_header_http, "test")

        instanceVoidData = VoidData()

        MTPConnector.voidRequest.return_value = instanceVoidData.get_void_request_fail_response()

        responseRefund = MTPConnector.voidRequest(
            instanceVoidData.get_refund_params)

        self.assertEquals(responseRefund['StatusCode'], 2013)

    @patch('todopagoconnector.TodoPagoConnector')
    def tets_get_void_request_702(self, MockTodoPagoConnector):
        j_header_http = {
            'Authorization': 'TODOPAGO f3d8b72c94ab4a06be2ef7c95490f7d3'
        }

        MTPConnector = MockTodoPagoConnector(j_header_http, "test")

        instanceVoidData = VoidData()

        MTPConnector.voidRequest.return_value = instanceVoidData.get_void_request_702_response()

        responseRefund = MTPConnector.voidRequest(
            instanceVoidData.get_refund_params)

        self.assertEquals(responseRefund['StatusCode'], 702)


if __name__ == '__main__':
    unittest.main()
