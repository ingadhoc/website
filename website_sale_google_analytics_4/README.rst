.. |company| replace:: ADHOC SA

.. |company_logo| image:: https://raw.githubusercontent.com/ingadhoc/maintainer-tools/master/resources/adhoc-logo.png
   :alt: ADHOC SA
   :target: https://www.adhoc.com.ar

.. |icon| image:: https://raw.githubusercontent.com/ingadhoc/maintainer-tools/master/resources/adhoc-icon.png

.. image:: https://img.shields.io/badge/license-AGPL--3-blue.png
   :target: https://www.gnu.org/licenses/agpl
   :alt: License: AGPL-3

======================
GA4 Ecommerce Tracking
======================

Self-contained Google Analytics 4 ecommerce tracking module for Odoo 19 websites.
Extends the native Odoo tracking with additional funnel events and adds
server-side event delivery via the GA4 Measurement Protocol — **no Google Tag
Manager required**.

Features
========

Frontend events (via ``gtag.js``)
----------------------------------

The following events are fired client-side, complementing the events already
covered by Odoo's native ``website_sale`` tracking (``view_item``,
``add_to_cart``, ``purchase``):

* ``view_cart`` – fired when the shopping cart page is loaded.
* ``begin_checkout`` – fired when the user clicks "Proceed to Checkout".
* ``add_shipping_info`` – fired when the user selects a delivery method on
  the checkout page.
* ``add_payment_info`` – fired when the user submits the payment form.
* ``remove_from_cart`` – fired when a cart line is deleted or its quantity is
  decremented.
* ``sign_up`` – fired when the registration form is submitted.
* ``login`` – fired when the login form is submitted.

Backend events (via GA4 Measurement Protocol)
----------------------------------------------

Server-side events are sent directly from Odoo to Google Analytics as a
reliability safeguard (ad-blockers, async/offline payments, etc.):

* ``purchase`` – sent after ``sale.order._action_confirm()``.
* ``refund`` – sent after a credit note (``out_refund`` invoice) is posted.

A scheduled action retries failed Measurement Protocol calls every 15 minutes
(up to 5 attempts per event).

Consent Mode v2 compatibility
-------------------------------

This module relies on Odoo's native gtag.js injection (``website.google_analytics_key``),
which already configures Consent Mode v2 with denied defaults and grants consent
when the user accepts optional cookies. No additional consent configuration is
required.

Installation
============

#. Install this module. It depends on ``website_sale`` and ``payment``.
#. Ensure the native Google Analytics Measurement ID has been configured in
   **Website → Configuration → Settings → Google Analytics** (field
   ``google_analytics_key``). This module shares that field.

Configuration
=============

#. Go to **Website → Configuration → Settings → Google Analytics**.
#. Set the **Measurement ID** (``G-XXXXXXXXXX``) in the existing
   **Google Analytics Key** field — this is the same field used by Odoo
   natively to inject the ``gtag.js`` snippet.
#. Set the **GA4 API Secret** in the new **GA4 Measurement Protocol API Secret**
   field. This secret is required for server-side event delivery.

   To generate an API secret: in the Google Analytics admin panel go to
   **Admin → Data collection and modification → Data Streams → your stream →
   Measurement Protocol API secrets → Create**.

   .. warning::
      The API secret must remain server-side only. Never expose it in the
      browser or client-side code.

#. *(Optional)* The scheduled action **GA4: Retry Failed MP Events** is
   created automatically and runs every 15 minutes. You can adjust the
   frequency in **Technical → Scheduled Actions**.

Usage
=====

Once configured, GA4 events are fired automatically with no further action
required from the store operator:

* **Cart events** are fired on the ``/shop/cart`` page.
* **Checkout funnel events** are fired as the customer progresses through
  address → delivery → payment steps.
* **Purchase events** are fired both client-side (via ``gtag.js``) and
  server-side (via Measurement Protocol) on order confirmation. GA4
  deduplicates these using the same ``transaction_id`` (the Odoo sale order
  numeric ID).
* **Refund events** are fired server-side when a credit note linked to a
  web order is confirmed.
* **Authentication events** are fired on the login/registration page.

GA session data (``_ga`` and ``_ga_<container>`` cookies) is captured from
the browser at the start of the checkout flow and stored on the sale order,
enabling proper session attribution for server-side events.

Known trade-offs
================

* **``value`` includes tax** – the event-level ``value`` parameter in all
  events uses ``amount_total`` (inclusive of tax and shipping) to stay
  consistent with Odoo's native tracking. The GA4 Measurement Protocol
  documentation recommends excluding tax and shipping from ``value``, so
  revenue figures may appear inflated if tax rates are significant. The
  event-level ``tax`` and ``shipping`` fields are still sent separately so
  the data can be reconciled.
* **GA client ID availability** – server-side events (``purchase``, ``refund``)
  require the customer to have been on the checkout page with JavaScript
  enabled so that the ``_ga`` cookie can be captured. Orders placed via the
  backend or via API will not have a ``ga_client_id`` and the MP event will be
  silently skipped.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/ingadhoc/website/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smash it by providing a detailed and welcomed feedback.

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
