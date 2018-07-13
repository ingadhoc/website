.. |company| replace:: ADHOC SA

.. |company_logo| image:: https://raw.githubusercontent.com/ingadhoc/maintainer-tools/master/resources/adhoc-logo.png
   :alt: ADHOC SA
   :target: https://www.adhoc.com.ar

.. |icon| image:: https://raw.githubusercontent.com/ingadhoc/maintainer-tools/master/resources/adhoc-icon.png

.. image:: https://img.shields.io/badge/license-AGPL--3-blue.png
   :target: https://www.gnu.org/licenses/agpl
   :alt: License: AGPL-3

================
Todopago Payment
================

Permite hacer pagos a traves de la pasarela de pago Todopago, solo valido para
pagos en pesos argentinos.

Installation
============

To install this module, you need to:

#. Only need to install the module

Configuration
=============

#. Go on to config / payment / payment methods / todpago
#. If you want to use it on sales order you should set "validation" to "automatic" (or you can create to payment adquires). The issue is that with "automatic", on payment return with status "pending", no message is displayed to the user regarding pending payment. (still not working)

*Notes:*

* "Mensaje de agradecimiento" on payment adquires is only displayed if payment is pending and adquires is of validation type "manual".
* If we choose to use validation = automatic, perhups we can post a message if validation is on pending (we should overwrite "payment_get_status")
* When paying from portal, not transaction is create do we get an error  with _todopago_form_get_tx_from_data method, we should check how other payment methods works


Usage
=====

*TEST MODE Y DESARROLLO*

Crear cuentas en: https://todopago.com.ar/. Entrar a herramietnas / comercios:
integración y generar credeciales ya sea para ambiente de producción o
ambiente de pruebas

Mas info en https://developers.todopago.com.ar/site/

Información de SANDBOX::

    'Authorization' = 'PRISMA A793D307441615AF6AAAD7497A75DE59'
    'SECURITY' = 'A793D307441615AF6AAAD7497A75DE59'
    'CURRENCYCODE' = 032
    'MERCHANT' = 2159
    'ENCODINGMETHOD' = 'XML'

Y::

    'END_POINT' = "https://developers.todopago.com.ar/services/t/1.1/"
    'Authorize' = "https://developers.todopago.com.ar/services/t/1.1/Authorize?wsdl"
    'PaymentMethods' = "https://developers.todopago.com.ar/services/t/1.1/PaymentMethods?wsdl"
    'Operations' = "https://developers.todopago.com.ar/services/t/1.1/Operations?wsdl"

**NOTA: Estos datos podrían variar, consultar https://developers.todopago.com.ar/site/sandbox de encontrar algún problema.**

Datos adicionales para control de fraude: https://github.com/TodoPago/SDK-Python#datos-adicionales-para-control-de-fraude

*Formas de pagar*

Datos de prueba desde https://developers.todopago.com.ar/site/datos-de-prueba

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
