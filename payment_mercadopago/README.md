# payment_mercadopago
MercadoPago payment module for Odoo 8.0 Ecommerce

## TEST MODE
Sobre sandbox
https://www.mercadopago.com.ar/developers/es/solutions/payments/basic-checkout/test/basic-sandbox/

Formas de pagar:
* Dinero en cuenta: El monto de dinero en cuenta es fijo. No se agota si lo usas en más de un pago y tampoco afecta tu saldo real. Para probar, ingresa cualquier clave y el estado será: approved.
* Tarjetas de crédito: Puedes usar cualquier código de seguridad. Para probar, elige una de las siguientes tarjetas de acuerdo al estado que quieras obtener:
    * Visa Nº 4444 4444 4444 0008: approved.
    * Mastercard Nº 5031 1111 1111 6619: approved.
    * Mastercard Nº 5031 1111 1111 6601: pending.
    * American Express Nº 37000 00000 02461: rejected.
    * Visa Nº 4444 4444 4444 0024: rejected.
* Boleto, depósito o cupón: Al probar, obtendrás el estado: pending.

URL para notificar pagos
https://www.mercadopago.com/mla/herramientas/notificaciones