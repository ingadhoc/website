==================================
Website Sale Express Checkout AR
==================================

Checkout de una sola página para el eCommerce argentino, con derivación de los
datos tributarios del lado del servidor.

Características
===============

- Colapsa el checkout del eCommerce en un único paso (``cart`` →
  ``express_checkout`` → ``payment``), despublicando los pasos nativos de
  dirección y de información extra.
- Se activa solo cuando la company del carrito tiene ``country_code == 'AR'`` y
  el website tiene habilitado el express checkout; en cualquier otro caso rige
  el flujo nativo de cuatro pasos, sin alteración.
- El comprador no toma ninguna decisión tributaria: la Responsabilidad ARCA y el
  tipo de documento se derivan del lado del servidor.
- Los campos tributarios derivados no se renderizan en ninguna forma y se
  descartan del payload entrante, por lo que un POST forjado no puede fijarlos.
- Sección "Factura A" que pide únicamente el CUIT; el resto de la información
  fiscal la resuelve el servidor (y el padrón de ARCA a través del bridge).
- El domicilio ``street2`` se ofrece detrás de un disclosure colapsado.
- Al habilitar el express checkout se fuerza la validación de facturas en
  background para la company.

Detalles Técnicos
=================

Modelos heredados
-----------------

- ``website``: campo ``enable_express_checkout``; override de
  ``_create_checkout_steps`` y ``write`` que sincronizan la publicación de los
  pasos por website mediante ``_sync_express_checkout_steps``; al habilitar se
  setea ``res.company.website_sale_background_post``.
- ``res.config.settings``: campo ``enable_express_checkout`` relacionado con el
  website.

Controlador
-----------

``WebsiteSaleExpressCheckout(WebsiteSale)``:

- ``GET /shop/express_checkout`` — render de la página única.
- ``POST /shop/express_checkout/submit`` — submit único; delega la creación del
  partner en ``_create_or_update_address`` (no la reimplementa) y arma el reparto
  de direcciones (Consumidor Final vs. Factura A).
- Overrides de ``_parse_form_data``, ``_get_mandatory_billing_address_fields`` y
  ``_complete_address_values``, acotados al flujo express vía
  ``request.express_checkout_flow``.
- Hook ``_express_apply_padron`` (no-op; lo implementa el bridge del padrón).

Datos
-----

- ``website.checkout.step`` genérico ``express_checkout`` (``step_href =
  /shop/express_checkout``).

Vistas
------

- ``res.config.settings`` — setting "Express Checkout (AR)".
- ``address_form_fields`` — view primario que hereda
  ``portal.address_form_fields``.
- ``express_checkout`` — página del checkout de una sola página.

Assets
------

- Interaction de frontend que extiende ``portal.customer_address`` (toggle de
  Factura A y validación del CUIT en vivo).

Hooks
-----

- ``post_init_hook`` — propaga el paso ``express_checkout`` a los websites
  existentes y sincroniza la publicación.
- ``uninstall_hook`` — elimina el paso express por website y republica los pasos
  nativos.

Uso
===

1. Instalar el módulo.
2. En Ajustes → Sitio web → eCommerce, activar "Express Checkout (AR)" en el
   website argentino. Esto reconfigura los pasos del checkout y habilita la
   validación de facturas en background de la company.
3. El comprador de la tienda completa la compra en una sola página con los datos
   mínimos; si necesita Factura A marca la casilla e ingresa su CUIT.

Arquitectura
============

El módulo reusa los métodos-hook nativos de ``portal`` / ``website_sale`` en
lugar de forkear controladores o templates: el submit pasa por
``_create_or_update_address`` (heredando las extensiones de las localizaciones) y
el template es un view primario que hereda ``portal.address_form_fields`` (por lo
que ``_get_combined_archs`` le aplica las contribuciones de los módulos de
localización). La reconfiguración del checkout se hace de forma declarativa sobre
``website.checkout.step`` (publicación por website), sin overrides del motor de
navegación.

Dependencias
============

- ``website_sale``
- ``l10n_ar_website_sale``
- ``website_sale_background_post``

Autor
=====

ADHOC SA

Licencia
========

AGPL-3
