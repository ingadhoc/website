# pylint: disable-all
# flake8: noqa
import sys
sys.path.append("..")
from todopagoconnector import TodoPagoConnector
from OperationByIdData import OperationByIdData
import unittest
from unittest import TestCase
if sys.version_info[0] >= 3:
    from unittest.mock import patch, Mock
else:
    from mock import patch, Mock, MagicMock


class GetOPertionByIdTest(TestCase):

    @patch('todopagoconnector.TodoPagoConnector')
    def test_get_ok(self, MockTodoPagoConnector):
        j_header_http = {
            'Authorization': 'TODOPAGO f3d8b72c94ab4a06be2ef7c95490f7d3'
        }

        MTPConnector = MockTodoPagoConnector(j_header_http, "test")

        instanceOperationBId = OperationByIdData()

        MTPConnector.getByOperationId.return_value = instanceOperationBId.get_request_ok_response()

        responseOperation = MTPConnector.getByOperationId(
            instanceOperationBId.get_operation_by_id_params())

        self.assertEquals(
            responseOperation['OperationsColections']['Operations']['RESULTCODE'], -1)

    @patch('todopagoconnector.TodoPagoConnector')
    def test_get_operation_fail(self, MockTodoPagoConnector):
        j_header_http = {
            'Authorization': 'TODOPAGO f3d8b72c94ab4a06be2ef7c95490f7d3'
        }

        MTPConnector = MockTodoPagoConnector(j_header_http, "test")

        instanceOperationBId = OperationByIdData()

        MTPConnector.getByOperationId.return_value = instanceOperationBId.get_request_fail_response()

        responseOperation = MTPConnector.getByOperationId(
            instanceOperationBId.get_operation_by_id_params_merchant_null)

        self.assertFalse(len(responseOperation['OperationsColections']))

    @patch('todopagoconnector.TodoPagoConnector')
    def test_get_operation_702(self, MockTodoPagoConnector):
        j_header_http = {
            'Authorization': 'TODOPAGO f3d8b72c94ab4a06be2ef7c95490f7d3'
        }

        MTPConnector = MockTodoPagoConnector(j_header_http, "test")

        instanceOperationBId = OperationByIdData()

        MTPConnector.getByOperationId.return_value = instanceOperationBId.get_request_702_response()

        responseOperation = MTPConnector.getByOperationId(
            instanceOperationBId.get_operation_by_id_params)

        self.assertEquals(
            responseOperation['OperationsColections']['Status'], 702)

    @patch('todopagoconnector.TodoPagoConnector')
    def test_get_operation_merchant_null(self, MockTodoPagoConnector):
        j_header_http = {
            'Authorization': 'TODOPAGO f3d8b72c94ab4a06be2ef7c95490f7d3'
        }

        MTPConnector = MockTodoPagoConnector(j_header_http, "test")

        instanceOperationBId = OperationByIdData()

        MTPConnector.getByOperationId.return_value = instanceOperationBId.get_request_merchant_null_response()

        responseOperation = MTPConnector.getByOperationId(
            instanceOperationBId.get_operation_by_id_params_merchant_null)

        self.assertEquals(
            responseOperation['OperationsColections']['Status'],
            1014)

if __name__ == '__main__':
    unittest.main()
