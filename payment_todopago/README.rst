payment_todopago
================
TodoPago payment module for Odoo 8.0 Ecommerce

Configuration
-------------
1. Install this module
2. Go on to config / payment / payment methods / todpago
3. If you want to use it on sales order you should set "validation" to "automatic" (or you can create to payment adquires). The issue is that with "automatic", on payment return with status "pending", no message is displayed to the user regarding pending payment. (still not working)

Notes:
* "Mensaje de agradecimiento" on payment adquires is only displayed if payment is pending and adquires is of validation type "manual".

Known issues / Roadmap
----------------------
1. improove return url, we should send it to mercadopago and have return data. perhups we can use additional_info and read it from mercadopago on response. Check mercadopago_back_no_return on 'main'
2. If we choose to use validation = automatic, perhups we can post a message if validation is on pending (we should overwrite "payment_get_status")
3. Implement ipn from https://www.mercadopago.com.ar/developers/es/api-docs/basic-checkout/ipn/
4. When paying from portal, not transaction is create do we get an error  with _mercadopago_form_get_tx_from_data method, we should check how other payment methods works

TEST MODE Y DESARROLLO
======================
Crear cuentas en:
https://todopago.com.ar/
Entrar a herramietnas / comercios: integración y generar credeciales ya sea para ambiente de producción o ambiente de pruebas

Mas info en https://developers.todopago.com.ar/site/

Información de SANDBOX:
    'Authorization' = 'PRISMA A793D307441615AF6AAAD7497A75DE59'
    'SECURITY' = 'A793D307441615AF6AAAD7497A75DE59'
    'CURRENCYCODE' = 032
    'MERCHANT' = 2159
    'ENCODINGMETHOD' = 'XML'

Y
    'END_POINT' = "https://developers.todopago.com.ar/services/t/1.1/"
    'Authorize' = "https://developers.todopago.com.ar/services/t/1.1/Authorize?wsdl"
    'PaymentMethods' = "https://developers.todopago.com.ar/services/t/1.1/PaymentMethods?wsdl"
    'Operations' = "https://developers.todopago.com.ar/services/t/1.1/Operations?wsdl"

Datos adicionales para contrl de fraude:
https://github.com/TodoPago/SDK-Python#datos-adicionales-para-control-de-fraude

Formas de pagar:
----------------
Datos de prueba desde https://developers.todopago.com.ar/site/datos-de-prueba
