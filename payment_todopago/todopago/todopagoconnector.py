# -*- coding: utf-8 -*-
# pip install suds-jurko
from suds.client import Client
import requests
import os.path
import urlparse
import sys
import copy
import urllib


def deprecated(func):
    """This is a decorator which can be used to mark
 functions as deprecated. It will result in a warning
 being emmitted when the function is used."""
    # def newFunc(*args, **kwargs):
    #     warnings.warn("Call to deprecated function %s." % func.__name__,
    #                   category=DeprecationWarning)
    #     return func(*args, **kwargs)
    #     newFunc.__name__ = func.__name__
    #     newFunc.__doc__ = func.__doc__
    #     newFunc.__dict__.update(func.__dict__)
    #     return newFunc


ver = '1.2.0'
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

#############################################


class TodoPagoConnector:

    def __init__(self, http_header, *mode):
        # mode deberia contener un solo valor, que
        # seria "test" o "prod", pero para mantener
        # retrocompatibilidad se aceptara que manden el wsdl
        # (este se ignorara) y el endpoint
        self._http_header = http_header
        # self._rest_http_header = http_header
        # self._rest_http_header['Accept'] = 'application/json'
        if len(mode) == 1:
            end_point = end_points_base[mode[0]]
        else:
            self._wsdls = mode[0]
            end_point = mode[1]
        self._end_point = end_point + soapAppend + tenant
        self._end_point_rest = end_point + tenant + restAppend
        self._end_point_rest_root = end_point + restAppend

    ###############################################
    # #######################################
    # ##Methodo publico que llama a la primera funcion
    # del servicio SendAuthorizeRequest###
    ####################################################
    # ##################################
    def sendAuthorize(self, options_comercio, options_operacion):
        return dict(self._sendAuthorizeRequest(
            options_comercio, options_operacion))

    @deprecated
    def sendAuthorizeRequest(self, options_comercio, options_operacion):
        return self._sendAuthorizeRequest(options_comercio, options_operacion)

    ##########################################
    # ###########################################
    # ##Methodo publico que llama a la segunda funcion
    #  del servicio GetAuthorizeRequest###
    ################################################
    # #####################################
    def getAuthorize(self, optionsAnwser):
        return self._parse_gaa(self._getAuthorizeAnswer(optionsAnwser))

    @deprecated
    def getAuthorizeAnswer(self, optionsAnwser):
        return self._getAuthorizeAnswer(optionsAnwser)

    ######################################
    # ###############################################
    # ##Methodo publico que llama a la segunda funcion
    #  del servicio GetAuthorizeRequest###
    ################################################
    # #####################################
    def returnRequest(self, optionsReturn):
        self._getClientSoap('Authorize')
        xml = self._parse_to_service(optionsReturn, 'ReturnRequest')

        return dict(
            self.cliente.service.ReturnRequest(__inject={'msg': xml}))

    ##############################################
    # #######################################
    # ##Methodo publico que llama a la segunda funcion
    # del servicio GetAuthorizeRequest###
    #####################################################
    # ################################
    def voidRequest(self, optionsVoid):
        self._getClientSoap('Authorize')
        xml = self._parse_to_service(optionsVoid, 'VoidRequest')

        return dict(
            self.cliente.service.VoidRequest(__inject={'msg': xml}))

    ################################################################
    # ##Methodo publico que descubre todas las promociones de pago###
    ################################################################
    def getAllPaymentMethods(self, optionsGAPM):
        self._getClientSoap('PaymentMethods')
        xml = self._parse_to_service(optionsGAPM, 'GetAll')

        return self.cliente.service.GetAll(__inject={'msg': xml})

    ################################################################
    # ##Methodo publico que devuelve el estado de una transaccion####
    ################################################################
    def getByOperationId(self, optionsGBOI):
        return self._do_rest(
            "Operations/GetByOperationId", optionsGBOI, keys_order_GBOI)

    @deprecated
    def getStatus(self, optionsGS):
        self._getClientSoap('Operations')
        xml = self._parse_to_service(optionsGS, 'GetByOperationId')

        return self.cliente.service.GetByOperationId(__inject={'msg': xml})

    ################################################################
    # ##Methodo publico que devuelve las transacciones en un rango###
    # ##de fechas y horas############################################
    ################################################################
    def getByRangeDateTime(self, optionsGBRDT):
        return self._do_rest(
            "Operations/GetByRangeDateTime",
            optionsGBRDT, keys_order_GBRDT)

    ################################################################
    # ##Methodo publico que devuelve las creddenciales###############
    ################################################################
    def getCredentials(self, user):
        return self._parse_rest_response(
            requests.post(self._end_point_rest_root+'Credentials',
                          data=user,
                          headers={'Accept': 'application/json'}))

    ########################
    # ##Metodos privados ####
    ########################
    def _sendAuthorizeRequest(
            self, options_comercio, options_operacion):
        payload = self._get_payload(options_operacion)
        options_comercio['Payload'] = payload
        xml = self._parse_to_service(
            options_comercio, 'SendAuthorizeRequest')
        self._getClientSoap('Authorize')

        return self.cliente.service.SendAuthorizeRequest(
            __inject={'msg': xml})

    def _getAuthorizeAnswer(self, optionsAnwser):
        self._getClientSoap('Authorize')
        xml = self._parse_to_service(
            optionsAnwser, 'GetAuthorizeAnswer')

        return self.cliente.service.GetAuthorizeAnswer(
            __inject={'msg': xml})

    def _parse_gaa(self, obj):
        data = dict(obj)
        payload = dict(data['Payload'])
        payload['Answer'] = dict(payload['Answer'])
        payload['Request'] = dict(payload['Request'])
        data['Payload'] = payload

        return data

    def _get_wsdl_url(self, filename):
        return urlparse.urljoin(
            'file:', urllib.pathname2url(
                os.path.abspath(
                    os.path.dirname(
                        __file__)))) + '/' + filename + '.wsdl'

    def _parse_to_service(self, data, servicio):
        retorno = """<soapenv:Envelope xmlns:soapenv=
        "http://schemas.xmlsoap.org/soap/envelope/"
        xmlns:api="http://api.todopago.com.ar">
        <soapenv:Header/><soapenv:Body>"""
        retorno += "<api:"+servicio+">"
        for key in data:
            retorno += "<api:"+key+">"+data[key]+"</api:"+key+">"
        retorno += "</api:"+servicio+">"
        retorno += """</soapenv:Body></soapenv:Envelope>"""

        return retorno

    def _getClientSoap(self, operacion):
        self.cliente = Client(self._get_wsdl_url(operacion),
                              location=self._end_point+operacion,
                              headers=self._http_header,
                              cache=None)

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
        except Exception:
            try:
                diccionario["LENGUAGEVERSION"] = sys.version()
            except Exception:
                diccionario["LENGUAGEVERSION"] = "version unknown"

        xmlpayload = "<Request>"
        for key in diccionario:
            xmlpayload += "<"+key+">"+diccionario[key]+"</"+key+">"
        xmlpayload += "</Request>"

        # print 'xmlpayload', xmlpayload
        return xmlpayload

    def _sort_rest_params(self, dict, keys_order):
        sorted_list = []
        for key in keys_order:
            sorted_list.append((key, dict[key]))

        return sorted_list

    def _parse_rest_params(self, params):
        url = ''
        for param in params:
            url += "/"+param[0]+"/"+param[1]

        return url

    def _parse_rest_response(self, response):
        return dict(response.json())

    def _do_rest(self, service, params, keys_order):
        sorted_params = self._sort_rest_params(params, keys_order)
        url = \
            self._end_point_rest + service + \
            self._parse_rest_params(sorted_params)

        headers_aux = copy.deepcopy(self._http_header)
        headers_aux["Accept"] = 'application/json'

        response = requests.get(url, headers=headers_aux)

        return self._parse_rest_response(response)
