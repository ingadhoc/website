======================================================
Website Sale Express Checkout AR - ARCA Padron Bridge
======================================================

Completa el partner de facturación del camino Factura A con los datos del padrón
de ARCA durante el express checkout.

Características
===============

- Cuando el comprador pide Factura A, consulta el padrón de ARCA en el submit y
  aplica al partner de facturación la razón social, el domicilio fiscal y la
  Responsabilidad ARCA que devuelva el padrón.
- La consulta tiene un timeout configurable (parámetro de sistema, 8 segundos por
  defecto); superado el tiempo, se conserva el default.
- Cualquier falla de la consulta (sin certificado, timeout, error del web
  service, CUIT ausente del padrón) se absorbe y se conserva la responsabilidad
  por defecto ya fijada por el módulo base, de modo que la compra se completa y la
  factura se emite igual (en background).
- Bridge de instalación automática: se instala solo cuando conviven el express
  checkout y la facturación electrónica argentina.

Detalles Técnicos
=================

Controlador
-----------

- ``WebsiteSaleExpressCheckout`` — override de ``_express_apply_padron``: llama a
  ``res.partner.get_data_from_padron_afip()``, limita el tiempo a nivel socket,
  captura cualquier excepción para conservar el default y escribe sobre el partner
  de facturación únicamente los campos fiscales (``name``, ``street``, ``city``,
  ``zip``, ``state_id``, ``l10n_ar_afip_responsibility_type_id``).

Parámetros de sistema
---------------------

- ``website_sale_express_checkout.padron_timeout`` — timeout de la consulta en
  segundos (default ``8``).

Uso
===

No requiere configuración: se instala automáticamente cuando están presentes
``website_sale_express_checkout`` y ``l10n_ar_edi_ux``, y actúa solo en el camino
Factura A del express checkout.

Arquitectura
============

Vive separado del módulo base porque ``l10n_ar_edi_ux`` es Enterprise y depende de
``account_accountant``: el módulo base no puede depender de eso. El bridge implementa
el hook ``_express_apply_padron`` que el base deja vacío.

Dependencias
============

- ``website_sale_express_checkout``
- ``l10n_ar_edi_ux``

Autor
=====

ADHOC SA

Licencia
========

AGPL-3
