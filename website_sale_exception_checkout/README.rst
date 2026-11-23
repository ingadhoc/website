===============================
Website Sale Exception Checkout
===============================

Valida las excepciones de venta en el último paso del checkout del e-commerce, antes del pago

Características
===============

- En el paso de pago (``/shop/payment``), evalúa las reglas de excepción de venta marcadas con "Check on eCommerce". Si alguna aplica, oculta los medios y el botón de pago y muestra un banner de error.
- El banner muestra el "eCommerce Message" de cada regla. Si está vacío, muestra un mensaje por defecto, sin el nombre interno de la regla.
- Agrega un botón "Back to cart" en el banner cuando hay excepciones.
- Las excepciones del e-commerce no se pueden ignorar desde el website.
- En las órdenes del e-commerce (con sitio web) solo se evalúan las reglas marcadas, en cualquier momento: checkout, confirmación después del pago, confirmación manual y ediciones posteriores. Las órdenes sin sitio web siguen evaluando todas las reglas.
- Se instala solo cuando están instalados ``website_sale`` y ``sale_exception``.

Detalles Técnicos
=================

- Modelos heredados:

  - ``exception.rule``: campos ``website_check`` (Boolean) y ``website_message`` (Html traducible); método ``_get_website_messages()``.
  - ``base.exception.method``: ``_rule_domain()`` filtra por ``website_check`` en ``sale.order`` y ``sale.order.line`` cuando todas las órdenes evaluadas tienen sitio web.
  - ``sale.order``: ``_get_website_exceptions()`` (evalúa con ``_get_exceptions()``, sin lanzar errores ni guardar las excepciones en la orden; ``sale_exception`` sí las guarda en las líneas) y ``_check_cart_is_ready_to_be_paid()``.

- Controller: ``WebsiteSale._get_shop_payment_errors()`` y ``_get_shop_payment_values()``.
- Vistas:

  - Form de ``exception.rule`` (hereda ``base_exception.view_exception_rule_form``).
  - Template ``website_sale.payment`` (botón "Back to cart").

Uso
===

#. Ir a la regla de excepción de venta (modelo "Sale order" o "Sale order line").
#. Marcar "Check on eCommerce".
#. Opcional: completar "eCommerce Message" con lo que tiene que hacer el cliente (por ejemplo, a qué número llamar).
#. En el e-commerce, cuando la regla aplica al carrito, el cliente ve el mensaje en el paso de pago y no puede pagar. Puede volver al carrito y modificarlo.

Arquitectura
============

- La validación usa el gancho nativo ``_get_shop_payment_errors()``: con errores, el template de pago ya oculta el formulario y el botón.
- ``_check_cart_is_ready_to_be_paid()`` repite la validación en ``/shop/payment/transaction``, que también usa el pago express.
- El alcance lo define la orden: si tiene ``website_id``, ``_rule_domain()`` limita las reglas a las marcadas. Si en un mismo lote hay órdenes con y sin sitio web (por ejemplo, una confirmación masiva), se evalúan todas las reglas.

Dependencias
============

- website_sale
- sale_exception

Autor
=====

ADHOC SA

Licencia
========

AGPL-3
