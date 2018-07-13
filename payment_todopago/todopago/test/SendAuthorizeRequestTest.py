# pylint: disable-all
# flake8: noqa
import sys
sys.path.append("..")
from todopagoconnector import TodoPagoConnector
from SendAuthorizeRequestData import SendAuthorizeRequestData
import unittest
from unittest import TestCase
if sys.version_info[0] >= 3:
    from unittest.mock import patch, Mock
else:
    from mock import patch, Mock, MagicMock


class SendAuthorizeRequestTest(TestCase):

    @patch('todopagoconnector.TodoPagoConnector')
    def test_get_credentials_ok(self, MockTodoPagoConnector):
        j_header_http = {
            'Authorization': 'TODOPAGO f3d8b72c94ab4a06be2ef7c95490f7d3'
        }

        MTPConnector = MockTodoPagoConnector(j_header_http, "test")

        instanceSARData = SendAuthorizeRequestData()

        MTPConnector.sendAuthorize.return_value = instanceSARData.send_authorize_request_ok_response()

        responseSAR = MTPConnector.sendAuthorize(
            instanceSARData.get_options_SAR_comercio_params(),
            instanceSARData.get_options_SAR_operation_params())

        self.assertEqual(responseSAR['StatusCode'], -1)

    @patch('todopagoconnector.TodoPagoConnector')
    def test_get_credentials_fail(self, MockTodoPagoConnector):
        j_header_http = {
            'Authorization': 'TODOPAGO f3d8b72c94ab4a06be2ef7c95490f7d3'
        }

        MTPConnector = MockTodoPagoConnector(j_header_http, "test")

        instanceSAR = SendAuthorizeRequestData()

        MTPConnector.sendAuthorize.return_value = instanceSAR.send_authorize_request_fail_response()

        responseSAR = MTPConnector.sendAuthorize(
            instanceSAR.get_options_SAR_comercio_params(),
            instanceSAR.get_options_SAR_operation_params())

        self.assertNotEquals(responseSAR['StatusCode'], -1)

    @patch('todopagoconnector.TodoPagoConnector')
    def test_get_credentials_702(self, MockTodoPagoConnector):
        j_header_http = {
            'Authorization': 'TODOPAGO f3d8b72c94ab4a06be2ef7c95490f7d3'
        }

        MTPConnector = MockTodoPagoConnector(j_header_http, "test")

        instanceSAR = SendAuthorizeRequestData()

        MTPConnector.sendAuthorize.return_value = instanceSAR.send_authorize_request_702_response()

        responseSAR = MTPConnector.sendAuthorize(
            instanceSAR.get_options_SAR_comercio_params(),
            instanceSAR.get_options_SAR_operation_params())

        self.assertNotEquals(responseSAR['StatusCode'], -1)

if __name__ == '__main__':
    unittest.main()
