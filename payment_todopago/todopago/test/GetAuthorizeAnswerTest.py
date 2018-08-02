# pylint: disable-all
# flake8: noqa
import sys
sys.path.append("..")
from todopagoconnector import TodoPagoConnector
from GetAuthorizeAnswerData import GetAuthorizeAnswerData
import unittest
from unittest import TestCase
if sys.version_info[0] >= 3:
    from unittest.mock import patch, Mock
else:
    from mock import patch, Mock, MagicMock


class GetAuthorizeAnswerTest(TestCase):

    @patch('todopagoconnector.TodoPagoConnector')
    def test_get_credentials_ok(self, MockTodoPagoConnector):
        j_header_http = {
            'Authorization': 'TODOPAGO f3d8b72c94ab4a06be2ef7c95490f7d3'
        }

        MTPConnector = MockTodoPagoConnector(j_header_http, "test")

        instanceGAAData = GetAuthorizeAnswerData()

        MTPConnector.getAuthorize.return_value = instanceGAAData.get_authorize_answer_ok_response()

        responseSAR = MTPConnector.getAuthorize(
            instanceGAAData.get_options_GAA_options_params())

        self.assertEqual(responseSAR['StatusCode'], -1)

    @patch('todopagoconnector.TodoPagoConnector')
    def test_get_credentials_fail(self, MockTodoPagoConnector):
        j_header_http = {
            'Authorization': 'TODOPAGO f3d8b72c94ab4a06be2ef7c95490f7d3'
        }

        MTPConnector = MockTodoPagoConnector(j_header_http, "test")

        instanceGAAData = GetAuthorizeAnswerData()

        MTPConnector.getAuthorize.return_value = instanceGAAData.get_authorize_answer_fail_response()

        responseSAR = MTPConnector.getAuthorize(
            instanceGAAData.get_options_GAA_options_params())

        self.assertNotEquals(responseSAR['StatusCode'], -1)

    @patch('todopagoconnector.TodoPagoConnector')
    def test_get_credentials_702(self, MockTodoPagoConnector):
        j_header_http = {
            'Authorization': 'TODOPAGO f3d8b72c94ab4a06be2ef7c95490f7d3'
        }

        MTPConnector = MockTodoPagoConnector(j_header_http, "test")

        instanceGAAData = GetAuthorizeAnswerData()

        MTPConnector.getAuthorize.return_value = instanceGAAData.get_authorize_answer_702_response()

        responseSAR = MTPConnector.getAuthorize(
            instanceGAAData.get_options_GAA_options_params())

        self.assertNotEquals(responseSAR['StatusCode'], -1)

if __name__ == '__main__':
    unittest.main()
