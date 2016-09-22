# -*- coding: utf-8 -*-
from. todopagoconnector import TodoPagoConnector

optionsSAR_comercio = {
    "Session": "ABCDEF-1234-12221-FDE1-00000200",
    "Security": "15406018567890AB40E46ABD10E",
    "EncodingMethod": "XML",
    "URL_OK": "http,//someurl.com/ok/",
    "URL_ERROR": "http,//someurl.com/fail/",
    "EMAILCLIENTE": "email_cliente@dominio.com"
}

optionsSAR_operacion = {
    "MERCHANT": "2266",
    "OPERATIONID": "06",
    "CURRENCYCODE": "032",
    "AMOUNT": "54",

    "CSBTCITY": "Villa General Belgrano",
    "CSSTCITY": "Villa General Belgrano",

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

optionsGAA = {
    'Security': '1234567890ABCDEF1234567890ABCDEF',
    'Merchant': "2153",
    'RequestKey': '0725b17e-3a0b-42f8-8b27-efb98b9e0b42',
    'AnswerKey': 'edb48330-29de-2544-f490-6db4b7d11abc'
}

optionsRR = {
    'Security': '1540601877567890AB240E46ABD10E',
    'Merchant': '2266',
    'RequestKey': 'c98617da-8536-51b4-41ae-859e8037d7ab',
    'AMOUNT': '1'
}

optionsVR = {
    'Security': '1540567890AB59EF50240E46ABD10E',
    'Merchant': '2266',
    'RequestKey': 'c98617da-8536-51b4-41ae-859e8037d7ab'
}
optionsGAPM = {
    'MERCHANT': '2153'
}
optionsGS = {
    'MERCHANT': '2658',
    'OPERATIONID': '8000'
}

optionsGBRDT = {
    'MERCHANT': '2866',
    'STARTDATE': '2015-11-01',
    'ENDDATE': '2015-12-10',
    'PAGENUMBER': '1'
}

j_header_http = {
    'Authorization': 'TODOPAGO 1540601877EB2059EF50240E46ABD10E'
}

j_wsdls = {
    'Operations': 'Operations',
    'Authorize': 'Authorize'
}

userCredenciales = {
    'USUARIO': "usuario@todopago.com",
    'CLAVE': "contrasena"
}

tpc = TodoPagoConnector(j_header_http, "test")
# print (tpc.sendAuthorize(optionsSAR_comercio, optionsSAR_operacion))
# print "\n\r ------------------------------------ "
# print tpc.getAuthorize(optionsGAA)
# print "\n\r ------------------------------------ "
# print tpc.returnRequest(optionsRR)
# print "\n\r ------------------------------------ "
# print tpc.voidRequest(optionsVR)
# print "\n\r ------------------------------------ "
# print tpc.getByOperationId(optionsGS)
# print "\n\r ------------------------------------ "
# print tpc.getByRangeDateTime(optionsGBRDT)
# print "\n\r ------------------------------------ "
# print tpc.getCredentials(userCredenciales)
# print "\n\r ------------------------------------ "
