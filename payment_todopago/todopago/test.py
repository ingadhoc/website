# pylint: disable-all
# flake8: noqa
from todopagoconnector import TodoPagoConnector
import sys    # sys.setdefaultencoding is cancelled by site.py
reload(sys)    # to re-enable sys.setdefaultencoding()
sys.setdefaultencoding('utf-8')
# import urllib para version 2 o 3
if sys.version_info[0] >= 3:
    from urllib.parse import urlparse
else:
    import urllib

j_header_http = {
    'Authorization': 'TODOPAGO f3d8b72c94ab4a06be2ef7c95490f7d3'
}

j_wsdls = {
    'Operations': 'Operations',
    'Authorize': 'Authorize'
}

# Datos de comercio
optionsSAR_comercio = {
    'Merchant': "2153",
    "Security": "f3d8b72c94ab4a06be2ef7c95490f7d3",
    "EncodingMethod": "XML",
    "URL_OK": "http,//someurl.com/ok/",
    "URL_ERROR": "http,//someurl.com/fail/",
    "EMAILCLIENTE": "email_cliente@dominio.com"
}
# fin Datos de comercio

# Control de Fraude
optionsSAR_operacion = {
    "MERCHANT": "2153",
    "OPERATIONID": "06",
    "CURRENCYCODE": "032",
    "AMOUNT": "3",

    "MININSTALLMENTS": "3",
    "MAXINSTALLMENTS": "6",
    "TIMEOUT": "300000",
    "AVAILABLEPAYMENTMETHODSIDS": "1#42#500",

    "CSBTCITY": "Villa General Belgrano",
    "CSSTCITY": "Villa General Belgrano",
    "CSMDD6": "",
    "CSBTCOUNTRY": "AR",
    "CSSTCOUNTRY": "AR",

    "CSBTEMAIL": "todopago@hotmail.com",
    "CSSTEMAIL": "todopago@hotmail.com",

    "CSBTFIRSTNAME": "Juan",
    "CSSTFIRSTNAME": "Juan",

    "CSBTLASTNAME": "Perez",
    "CSSTLASTNAME": "Perez",

    "CSBTPHONENUMBER": "541160913988",
    "CSSTPHONENUMBER": "541160913988",

    "CSBTPOSTALCODE": "1010",
    "CSSTPOSTALCODE": "1010",

    "CSBTSTATE": "B",
    "CSSTSTATE": "B",

    "CSBTSTREET1": "Cerrito 740",
    "CSSTSTREET1": "Cerrito 740",


    "CSBTSTREET2": "Cerrito 740",
    "CSSTSTREET2": "Cerrito 740",

    "CSBTCUSTOMERID": "453458",
    "CSBTIPADDRESS": "192.0.0.4",
    "CSPTCURRENCY": "ARS",
    "CSPTGRANDTOTALAMOUNT": "125.38",
    "CSMDD7": "",
    "CSMDD8": "Y",
    "CSMDD9": "",
    "CSMDD10": "",
    "CSMDD11": "",
    "STCITY": "rosario",
    "STCOUNTRY": "",
    "STEMAIL": "jose@gmail.com",
    "STFIRSTNAME": "Jose",
    "STLASTNAME": "Perez",
    "STPHONENUMBER": "541155893737",
    "STPOSTALCODE": "1414",
    "STSTATE": "D",
    "STSTREET1": "San Martin 123",
    "CSMDD12": "",
    "CSMDD13": "",
    "CSMDD14": "",
    "CSMDD15": "",
    "CSMDD16": "",
    "CSITPRODUCTCODE": "electronic_good",
    "CSITPRODUCTDESCRIPTION": "NOTEBOOK L845 SP4304LA DF TOSHIBA",
    "CSITPRODUCTNAME": "NOTEBOOK L845 SP4304LA DF TOSHIBA",
    "CSITPRODUCTSKU": "LEVJNSL36GN",
    "CSITTOTALAMOUNT": "1254.40",
    "CSITQUANTITY": "1",
    "CSITUNITPRICE": "1254.40"
}

tpc = TodoPagoConnector(j_header_http, "test")

print('--------------------- SAR RESPONSE ---------------------')

resultSAR = tpc.sendAuthorize(optionsSAR_comercio, optionsSAR_operacion)

encoding = sys.stdout.encoding

if (encoding == None):
    encoding = "cp850"

# show service result
for k, val in resultSAR.items():
    print(str(k)+": " + str(val))


print('--------------------- GAA RESPONSE ---------------------')

# Datos de comercio
optionsAnswer = {
    "Security": "f3d8b72c94ab4a06be2ef7c95490f7d3",
    "Merchant": "2153",
    "RequestKey": "a2fc7d9e-7c7d-8a55-5322-cecb593160d3",
    "AnswerKey": "2ac51ee1-1e34-19aa-61bc-3c80407fbbc3"
}

resultGAA = tpc.getAuthorize(optionsAnswer)

print(resultGAA)


print('--------------------- ALLPAYMENTMETHODS ---------------------')

optionsPaymentMethods = {
    "MERCHANT": "12541"
}

resultGetOperationById = tpc.getAllPaymentMethods(optionsPaymentMethods)

print(resultGetOperationById)

print('--------------------- DISCOVER PAYMENT METHODS ---------------------')

resultGetOperationById = tpc.discoverPaymentMethods()

print(resultGetOperationById)


print('--------------------- GETOPERATIONBYID ---------------------')

optionsGOBI = {
    "MERCHANT": "2153",
    "OPERATIONID": "02"
}

responGOBI = tpc.getByOperationId(optionsGOBI)

print(responGOBI)


print('--------------------- DEVOLUCIONES ---------------------')

optionsReturnRequest = {
    "Merchant": "2153",
    "Security": "f3d8b72c94ab4a06be2ef7c95490f7d3",
    "RequestKey": "a2fc7d9e-7c7d-8a55-5322-cecb593160d3",
    "AMOUNT": "1.00"
}

responseReturnRequest = tpc.returnRequest(optionsReturnRequest)

print(responseReturnRequest)


print('--------------------- ANULACION ---------------------')

optionsVoidRequest = {
    "Merchant": "2153",
    "Security": "f3d8b72c94ab4a06be2ef7c95490f7d3",
    "RequestKey": "a2fc7d9e-7c7d-8a55-5322-cecb593160d3"
}

responseVoidRequest = tpc.voidRequest(optionsVoidRequest)

print(responseVoidRequest)


print('--------------------- GET RANGE BY DATE ---------------------')

optionsGBRDT = {
    "MERCHANT": "2153",
    "STARTDATE": "2016-01-01",
    "ENDDATE": "2016-02-19",
    "PAGENUMBER": "1"
}

responseGetByRange = tpc.getByRangeDateTime(optionsGBRDT)

print(responseGetByRange)


print('--------------------- GET CREDENTIALS ---------------------')

UserAccount = {
    'USUARIO': "usuario@gmail.com",
    'CLAVE': "pass123!"
}

responseGetCredential = tpc.getCredentials(UserAccount)

print(responseGetCredential)
