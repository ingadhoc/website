.. |company| replace:: ADHOC SA

.. |company_logo| image:: https://raw.githubusercontent.com/ingadhoc/maintainer-tools/master/resources/adhoc-logo.png
   :alt: ADHOC SA
   :target: https://www.adhoc.com.ar

.. |icon| image:: https://raw.githubusercontent.com/ingadhoc/maintainer-tools/master/resources/adhoc-icon.png

.. image:: https://img.shields.io/badge/license-AGPL--3-blue.png
   :target: https://www.gnu.org/licenses/agpl
   :alt: License: AGPL-3

===========================
Website Sale Cart Offcanvas
===========================

Show the cart in a side panel (Bootstrap offcanvas) when a product is added and when the
header cart icon is clicked, instead of the standard toast notification.

Features
========

* Adds a third value, *Open cart panel*, to the per website *Add to Cart* setting. The
  default (*Stay on Product Page*) is unchanged, and with the other two values the website
  behaves exactly as standard Odoo: no extra request and no extra node in the page.
* The panel opens from every "add to cart" origin: product page, *Add to Cart* snippet,
  dynamic product carousel, suggested accessories, wishlist and comparison page. With
  variants, optional products or combos it opens after the configurator dialog is
  confirmed.
* The header cart icon opens the panel instead of navigating to ``/shop/cart``, on desktop
  and on mobile. The link is kept, so without JavaScript it still navigates.
* The panel is read only: lines, totals and a *Checkout* button to ``/shop/cart``. Totals
  are rendered with ``website_sale.total``, so they always match the cart page.
* It stays open until the visitor closes it, with the backdrop, the close button or ``Esc``.
* On the cart page the panel does not open: adding a product there refreshes the page as
  usual.
* Cart warnings (out of stock, invalid combo) keep using the standard notification.

Technical details
=================

* ``website``: ``add_to_cart_action`` gains the ``open_offcanvas`` value through
  ``selection_add``. The value reaches the frontend through the session info that
  ``website_sale`` already publishes.
* Controller route ``/shop/cart/offcanvas`` (``jsonrpc``, ``auth="public"``), which returns
  the rendered panel content and the cart quantity. The cart HTML never travels inside the
  page, only over this route, so a page cache cannot serve one visitor's cart to another.
* Views: ``cart_offcanvas`` inherits ``website.layout`` and adds the empty panel;
  ``cart_offcanvas_content`` is the fragment returned by the route.
* Frontend: a patch on ``CartService._showCartNotification``, plus two interactions, one on
  the panel (fills it on ``show.bs.offcanvas``) and one on the header cart icon.

Installation
============

To install this module, you need to:

#. Just install it.

Configuration
=============

To configure this module, you need to:

#. Go to *Website > Configuration > Settings*.
#. Select the website you want to configure.
#. Under *Shop - Checkout Process*, set *Add to Cart* to *Open cart panel*.

Usage
=====

#. Browse the shop and add a product to the cart: the side panel opens with the cart
   content.
#. Click the cart icon in the header at any time to review the cart without leaving the
   page.
#. Click *Checkout* in the panel to go to ``/shop/cart``.

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
