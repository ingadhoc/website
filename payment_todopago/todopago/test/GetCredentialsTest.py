# pylint: disable-all
# flake8: noqa
import sys
sys.path.append("..")
from todopagoconnector import TodoPagoConnector
from CredentialsData import CredentialsData
import unittest
from unittest import TestCase
if sys.version_info[0] >= 3:
    from unittest.mock import patch, Mock
else:
    from mock import patch, Mock, MagicMock


class CredentialsTest(TestCase):

    @patch('todopagoconnector.TodoPagoConnector')
    def test_get_credentials_ok(self, MockTodoPagoConnector):
        j_header_http = {
            'Authorization': 'TODOPAGO f3d8b72c94ab4a06be2ef7c95490f7d3'
        }

        MTPConnector = MockTodoPagoConnector(j_header_http, "test")

        instanceCredential = CredentialsData()

        MTPConnector.getCredentials.return_value = instanceCredential.get_credentials_ok_response()

        UserAccount = {
            'USUARIO': "usuario@gmail.com",
            'CLAVE': "1970Stk!"
        }

        responseGetCredential = MTPConnector.getCredentials(UserAccount)

        self.assertEquals(
            responseGetCredential['Credentials']['resultado']
            ['codigoResultado'],
            0)
        self.assertTrue(len(responseGetCredential['Credentials']['merchantId']))
        self.assertTrue(len(responseGetCredential['Credentials']['APIKey']))

    @patch('todopagoconnector.TodoPagoConnector')
    def test_get_credentials_user_empty(self, MockTodoPagoConnector):
        j_header_http = {
            'Authorization': 'TODOPAGO f3d8b72c94ab4a06be2ef7c95490f7d3'
        }

        MTPConnector = MockTodoPagoConnector(j_header_http, "test")

        instanceCredential = CredentialsData()

        MTPConnector.getCredentials.return_value = instanceCredential.get_credentials_wrong_user_response()

        UserAccount = {
            'USUARIO': "usuario@gmail.com",
            'CLAVE': "pass123"
        }

        responseGetCredential = MTPConnector.getCredentials(UserAccount)

        self.assertEquals(
            responseGetCredential['Credentials']['resultado']
            ['codigoResultado'],
            1050)
        self.assertFalse(
            len(responseGetCredential['Credentials']['merchantId']))
        self.assertFalse(len(responseGetCredential['Credentials']['APIKey']))

    @patch('todopagoconnector.TodoPagoConnector')
    def test_get_credentials_pass_empty(self, MockTodoPagoConnector):
        j_header_http = {
            'Authorization': 'TODOPAGO f3d8b72c94ab4a06be2ef7c95490f7d3'
        }

        MTPConnector = MockTodoPagoConnector(j_header_http, "test")

        instanceCredential = CredentialsData()

        MTPConnector.getCredentials.return_value = instanceCredential.get_credentials_wrong_password_response()

        UserAccount = {
            'USUARIO': "usuario@gmail.com",
            'CLAVE': ""
        }

        responseGetCredential = MTPConnector.getCredentials(UserAccount)

        self.assertEquals(
            responseGetCredential['Credentials']['resultado']
            ['codigoResultado'],
            1055)
        self.assertFalse(
            len(responseGetCredential['Credentials']['merchantId']))
        self.assertFalse(len(responseGetCredential['Credentials']['APIKey']))

if __name__ == '__main__':
    unittest.main()
