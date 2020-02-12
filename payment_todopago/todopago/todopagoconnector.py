# flake8: noqa
import requests
import os.path
import sys
import warnings
import copy
import json
from suds.client import Client
from suds.sax.text import Raw

# import urllib para version 2 o 3
if sys.version_info[0] >= 3:
    from urllib import parse
    from urllib import request
else:
    import urllib


def deprecated(func):
    """This is a decorator which can be used to mark functions
    as deprecated. It will result in a warning being emmitted
    when the function is used."""
    def newFunc(*args, **kwargs):
        warnings.warn("Call to deprecated function %s." % func.__name__,
                      category=DeprecationWarning)
        return func(*args, **kwargs)
    newFunc.__name__ = func.__name__
    newFunc.__doc__ = func.__doc__
    newFunc.__dict__.update(func.__dict__)

    return newFunc


ver = '1.7.0'
soapAppend = 'services/'
restAppend = 'api/'
tenant = 't/1.1/'
soapAthorizeAppend = 'Authorize'
end_points_base = {
    "test": "https://developers.todopago.com.ar/",
    "prod": "https://apis.todopago.com.ar/"
}

keys_order_GBRDT = (
    'MERCHANT',
    'STARTDATE',
    'ENDDATE',
    'PAGENUMBER'
)
keys_order_GBOI = (
    'MERCHANT',
    'OPERATIONID'
)

keys_order_GAPM = {
    'MERCHANT'
}
#############################################


class TodoPagoConnector:

    def __init__(self, http_header, *mode):
        # mode deberia contener un solo valor, que seria "test" o "prod", pero para mantener retrocompatibilidad se aceptara que manden el wsdl (este se ignorara) y el endpoint
        self._http_header = http_header
        #self._rest_http_header = http_header
        #self._rest_http_header['Accept'] = 'application/json'
        if(len(mode) == 1):
            end_point = end_points_base[mode[0]]
        else:
            self._wsdls = mode[0]
            end_point = mode[1]
        self._end_point = end_point + soapAppend + tenant
        self._end_point_rest = end_point + tenant + restAppend
        self._end_point_rest_root = end_point + restAppend

    ######################################################################################
    ###Methodo publico que llama a la primera funcion del servicio SendAuthorizeRequest###
    ######################################################################################
    def sendAuthorize(self, options_comercio, options_operacion):
        return dict(self._sendAuthorizeRequest(
            options_comercio, options_operacion))

    @deprecated
    def sendAuthorizeRequest(self, options_comercio, options_operacion):
        return self._sendAuthorizeRequest(options_comercio, options_operacion)

    #####################################################################################
    ###Methodo publico que llama a la segunda funcion del servicio GetAuthorizeRequest###
    #####################################################################################
    def getAuthorize(self, optionsAnwser):
        result = self._parse_gaa(self._getAuthorizeAnswer(optionsAnwser))
        return result

    @deprecated
    def getAuthorizeAnswer(self, optionsAnwser):
        return self._getAuthorizeAnswer(optionsAnwser)

    #####################################################################################
    ###Methodo publico que llama a la devolucion###
    #####################################################################################
    def returnRequest(self, optionsReturn):
        self._getClientSoap('Authorize')
        xml = self._parse_to_service(optionsReturn, 'ReturnRequest')
        xmlFormat = Raw(xml)

        return dict(self.cliente.service.ReturnRequest(xmlFormat))

    #####################################################################################
    ###Methodo publico que llama a la anulacion###
    #####################################################################################
    def voidRequest(self, optionsVoid):
        self._getClientSoap('Authorize')
        xml = self._parse_to_service(optionsVoid, 'VoidRequest')
        xmlFormat = Raw(xml)

        return dict(self.cliente.service.VoidRequest(xmlFormat))

    ################################################################
    ###Methodo publico que descubre todas las promociones de pago###
    ################################################################
    def getAllPaymentMethods(self, optionsGAPM):
        return self._do_rest("PaymentMethods/Get", optionsGAPM, keys_order_GAPM)

    ################################################################
    ###Methodo publico que descubre todas los medios de pago     ###
    ################################################################
    def discoverPaymentMethods(self):
        return self._do_rest("PaymentMethods/Discover", None, {})

    ################################################################
    ###Methodo publico que devuelve el estado de una transaccion####
    ################################################################
    def getByOperationId(self, optionsGBOI):
        return self._do_rest(
            "Operations/GetByOperationId", optionsGBOI, keys_order_GBOI)

    @deprecated
    def getStatus(self, optionsGS):
        self._getClientSoap('Operations')
        xml = self._parse_to_service(optionsGS, 'GetByOperationId')
        xmlFormat = Raw(xml)

        return self.cliente.service.GetByOperationId(xmlFormat)

    ################################################################
    ###Methodo publico que devuelve las transacciones en un rango###
    ###de fechas y horas############################################
    ################################################################
    def getByRangeDateTime(self, optionsGBRDT):
        return self._do_rest(
            "Operations/GetByRangeDateTime", optionsGBRDT, keys_order_GBRDT)

        ################################################################
    ###Methodo publico que devuelve las creddenciales###############
    ################################################################
    def getCredentials(self, user):
        return self._parse_rest_response(
            requests.post(
                self._end_point_rest_root + 'Credentials', data=json.dumps(user),
                headers={'Content-Type': 'application/json'},
                verify=False))

    ########################
    ###Metodos privados ####
    ########################
    def _sendAuthorizeRequest(self, options_comercio, options_operacion):
        payload = self._get_payload(options_operacion)
        options_comercio['Payload'] = payload
        xml = self._parse_to_service(options_comercio, 'SendAuthorizeRequest')
        xmlFormat = Raw(xml)

        self._getClientSoap('Authorize')

        return self.cliente.service.SendAuthorizeRequest(xmlFormat)

    def _getAuthorizeAnswer(self, optionsAnwser):
        self._getClientSoap('Authorize')
        xml = self._parse_to_service(optionsAnwser, 'GetAuthorizeAnswer')
        xmlFormat = Raw(xml)

        return self.cliente.service.GetAuthorizeAnswer(xmlFormat)

    def _parse_gaa(self, obj):
        data = dict(obj)

        return data

    def _get_wsdl_url(self, filename):
        url = 'file:///'+os.path.realpath(os.path.join(
            os.getcwd(), os.path.dirname(__file__)))+'/wsdl/'+filename+'.wsdl'

        return url

    def _parse_to_service(self, data, servicio):
        retorno = """<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:api="http://api.todopago.com.ar"><soapenv:Header/><soapenv:Body>"""
        retorno += "<api:"+servicio+">"
        for key in data:
            retorno += "<api:"+key+">"+data[key]+"</api:"+key+">"
        retorno += "</api:"+servicio+">"
        retorno += """</soapenv:Body></soapenv:Envelope>"""

        return retorno

    def _getClientSoap(self, operacion):
        self.cliente = Client(self._get_wsdl_url(operacion),  # se tiene que extraer de un array
                              location=self._end_point+operacion,  # se tiene que aprmar segun la funcion
                              headers=self._http_header,
                              cache=None,
                              nosend=False)

    def _client_soap_header(self, data):
        retorno = "{"
        for key in data:
            retorno += key+" : '"+data[key]+"', "
        retorno += "}, "

        return retorno

    def _get_payload(self, diccionario):
        diccionario["SDK"] = "Python"
        diccionario["SDKVERSION"] = ver
        try:
            diccionario["LENGUAGEVERSION"] = sys.version
        except Exception as err:
            try:
                diccionario["LENGUAGEVERSION"] = sys.version()
            except Exception as err2:
                diccionario["LENGUAGEVERSION"] = "version unknown"

        # NOTE: added in order to avoid <ApplicationIdentification/> not mapped to message part error
        diccionario["LENGUAGEVERSION"] = diccionario["LENGUAGEVERSION"].replace(
            '\n', '')

        xmlpayload = "<Request>"
        for key in diccionario:
            xmlpayload += "<"+key+">"+diccionario[key]+"</"+key+">"
        xmlpayload += "</Request>"

        return xmlpayload

    def _sort_rest_params(self, data, keys_order):
        sorted_list = []
        for key in keys_order:
            sorted_list.append((key, data[key]))

        return sorted_list

    def _parse_rest_params(self, params):
        url = ''
        for param in params:
            # param[0] tendra la key y param [1] el value
            url += "/"+param[0]+"/"+param[1]

        return url

    def _parse_rest_response(self, response):
        return dict(response.json())

    def _do_rest(self, service, params, keys_order):
        sorted_params = self._sort_rest_params(params, keys_order)
        url = self._end_point_rest + service + \
            self._parse_rest_params(sorted_params)

        # print(self._http_header)
        headers_aux = copy.deepcopy(self._http_header)
        headers_aux['Accept'] = 'application/json'

        response = requests.get(url, headers=headers_aux, verify=False)

        return self._parse_rest_response(response)
