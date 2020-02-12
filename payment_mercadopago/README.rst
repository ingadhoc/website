.. |company| replace:: ADHOC SA

.. |company_logo| image:: https://raw.githubusercontent.com/ingadhoc/maintainer-tools/master/resources/adhoc-logo.png
   :alt: ADHOC SA
   :target: https://www.adhoc.com.ar

.. |icon| image:: https://raw.githubusercontent.com/ingadhoc/maintainer-tools/master/resources/adhoc-icon.png

.. image:: https://img.shields.io/badge/license-AGPL--3-blue.png
   :target: https://www.gnu.org/licenses/agpl
   :alt: License: AGPL-3

===================
Mercadopago Payment
===================

Permite hacer pagos a traves de la pasarela de pago Mercadopago.

Installation
============

To install this module, you need to:

#. Only need to install the module

Configuration
=============

#. Go on to config / payment / payment methods / mercadopago
#. If you want to use it on sales order you should set "validation" to "automatic" (or you can create to payment adquires). The issue is that with "automatic", on payment return with status "pending", no message is displayed to the user regarding pending payment. (still not working)

*Notes:*

* "Mensaje de agradecimiento" on payment adquires is only displayed if payment is pending and adquires is of validation type "manual".
* If we choose to use validation = automatic, perhups we can post a message if validation is on pending (we should overwrite "payment_get_status")
* When paying from portal, not transaction is create do we get an error  with _mercadopago_form_get_tx_from_data method, we should check how other payment methods works

Usage
=====

TEST MODE
---------

Sobre sandbox
https://www.mercadopago.com.ar/developers/es/solutions/payments/basic-checkout/test/basic-sandbox/


Formas de pagar:
----------------

* Dinero en cuenta: El monto de dinero en cuenta es fijo. No se agota si lo usas en más de un pago y tampoco afecta tu saldo real. Para probar, ingresa cualquier clave y el estado será: approved.
* Tarjetas de crédito: Puedes usar cualquier código de seguridad. Para probar, elige una de las siguientes tarjetas de acuerdo al estado que quieras obtener:

  * Visa N°4170 0688 1010 8020 (cvv 123, fecha vencimiento 11/25)
  * Mastercard N° 5031 7557 3453 0604 (cvv 123, fecha vencimiento 11/25)
  * American Express N° 3711 8030 3257 522 (cvv 1234, fecha vencimiento 11/25)
  * Más tarjetas de pruebas en https://www.mercadopago.com.ar/developers/es/guides/localization/local-cards/

* Boleto, depósito o cupón: Al probar, obtendrás el estado: pending.

URL para notificar pagos: https://www.mercadopago.com/mla/herramientas/notificaciones

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: http://runbot.adhoc.com.ar/

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/ingadhoc/website/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed feedback.

Credits
=======

Images
------

* |company| |icon|

Contributors
------------

Maintainer
----------

|company_logo|

This module is maintained by the |company|.

To contribute to this module, please visit https://www.adhoc.com.ar.
