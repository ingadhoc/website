# pylint: disable-all
# flake8: noqa
class CredentialsData:

    def get_credentials_ok_response(self):
        return {
            "Credentials": {
                "codigoResultado": 1,
                "resultado": {
                    "codigoResultado": 0,
                    "mensajeKey": "",
                    "mensajeResultado": "Aceptado"
                },
                "merchantId": "5963",
                "APIKey": "TODOPAGO 1f5a522cb9a349c68f8e9e7ac8d0db11"
            }
        }

    def get_credentials_wrong_user_response(self):
        return {
            "Credentials": {
                "codigoResultado": 1,
                "resultado": {
                    "codigoResultado": 1050,
                    "mensajeKey": 1050,
                    "mensajeResultado": "asasd"
                },
                "merchantId": "",
                "APIKey": ""
            }
        }

    def get_credentials_wrong_password_response(self):
        return {
            "Credentials": {
                "codigoResultado": 1,
                "resultado": {
                    "codigoResultado": 1055,
                    "mensajeKey": 1055,
                    "mensajeResultado": "asasdasd"
                },
                "merchantId": "",
                "APIKey": ""
            }
        }
