payment_mercadopago
===================
MercadoPago payment module for Odoo 8.0 Ecommerce


Configuration
-------------

1. Install this module
2. Go on to config / payment / payment methods / mercadopago
3. If you want to use it on sales order you should set "validation" to "automatic" (or you can create to payment adquires). The issue is that with "automatic", on payment return with status "pending", no message is displayed to the user regarding pending payment. (still not working)

Notes:
* "Mensaje de agradecimiento" on payment adquires is only displayed if payment is pending and adquires is of validation type "manual".

Known issues / Roadmap
----------------------

1. improove return url, we should send it to mercadopago and have return data. perhups we can use additional_info and read it from mercadopago on response. Check mercadopago_back_no_return on 'main'
2. If we choose to use validation = automatic, perhups we can post a message if validation is on pending (we should overwrite "payment_get_status")
3. Implement ipn from https://www.mercadopago.com.ar/developers/es/api-docs/basic-checkout/ipn/
4. When paying from portal, not transaction is create do we get an error  with _mercadopago_form_get_tx_from_data method, we should check how other payment methods works


TEST MODE
=========

Sobre sandbox
https://www.mercadopago.com.ar/developers/es/solutions/payments/basic-checkout/test/basic-sandbox/


Formas de pagar:
----------------

* Dinero en cuenta: El monto de dinero en cuenta es fijo. No se agota si lo usas en más de un pago y tampoco afecta tu saldo real. Para probar, ingresa cualquier clave y el estado será: approved.
* Tarjetas de crédito: Puedes usar cualquier código de seguridad. Para probar, elige una de las siguientes tarjetas de acuerdo al estado que quieras obtener:

IMPORTANTE: el sandbox parece no estar andando bien como se dice acá https://www.mercadopago.com.ar/developers/es/solutions/payments/basic-checkout/test y recomiendan usar estas tarjetas para probar https://www.mercadopago.com.ar/developers/es/solutions/payments/basic-checkout/test/test-payments/

  * Visa Nº 4444 4444 4444 0008: approved.
  * Mastercard Nº 5031 1111 1111 6619: approved.
  * Mastercard Nº 5031 1111 1111 6601: pending.
  * American Express Nº 37000 00000 02461: rejected.
  * Visa Nº 4444 4444 4444 0024: rejected.

* Boleto, depósito o cupón: Al probar, obtendrás el estado: pending.

URL para notificar pagos: https://www.mercadopago.com/mla/herramientas/notificaciones
