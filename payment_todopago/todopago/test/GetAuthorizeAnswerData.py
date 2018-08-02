# pylint: disable-all
# flake8: noqa
class GetAuthorizeAnswerData:

    def get_options_GAA_options_params(self):
        return {
            "Security": "8A891C0676A25FBF052D1C2FFBC82DEE",
            "Merchant": "41702",
            "RequestKey": "83765ffb-39c8-2cce-b0bf-a9b50f405ee3",
            "AnswerKey": "9c2ddf78-1088-b3ac-ae5a-ddd45976f77d"
        }

    def get_authorize_answer_ok_response(self):
        return {
            "RequestKey": "20c8abb6-343f-eb40-d524-84b464be0c27",
            "PublicRequestKey": "t48ae3e60-5cb0-9fb1-7608-4cff0c83f24b",
            "URL_Request": "https://developers.todopago.com.ar/formulario/commands?command=formulario&m=t48ae3e60-5cb0-9fb1-7608-4cff0c83f24b",
            "StatusMessage": "Solicitud de Autorizacion Registrada",
            "StatusCode": -1
        }

    def get_authorize_answer_fail_response(self):
        return {
            "StatusCode": 98001,
            "StatusMessage": "El campo CSBTCITY es obligatorio."
        }

    def get_authorize_answer_702_response(self):
        return {
            "StatusCode": 702,
            "StatusMessage": "Cuanta de Vendedor Invalida"
        }
