====================================
Website Sale Stock Hide Unavailable
====================================

Let each website decide what the shop does with storable products that are out
of stock and cannot be sold out of stock: show them (Odoo's default), push them
to the end of the listing, or hide them from the listing, the site search, the
sitemap, the accessory/alternative blocks and the per-category product count.

The product page always keeps responding 200, so indexed URLs and SEO are not
lost during a temporary stock break.

Availability is precomputed in the backend (a small table of *unavailable*
products per warehouse scope) and the storefront only adds a SQL sub-query to
the domain it already builds. Nothing in the hot request path computes stock.

.. contents::
   :local:

Configuration
=============

Go to *Website ‣ Configuration ‣ Settings*, pick a website and set **Out-of-Stock
Products**:

* **Show** (default): identical to standard Odoo.
* **Show at the end of the list**: out-of-stock products appear last, in any sort
  order, still listed in search and sitemap.
* **Hide**: out-of-stock products disappear from listing, search, sitemap,
  accessories/alternatives and category counts.

A product is a candidate to be hidden or pushed down only when it is published,
storable, has "Sell when Out-of-Stock" disabled and has a single variant.

The warehouse scope follows the website's **Warehouse** setting: a specific
warehouse, or, when left empty, the whole company.

Usage
=====

The precomputed data is kept up to date by two scheduled actions:

* *E-commerce: Drain out-of-stock recompute queue* — runs every 5 minutes and
  reflects stock changes. Change its interval to tune the freshness window.
* *E-commerce: Full sweep out-of-stock availability* — runs nightly and
  reconciles every candidate regardless of the queue.

When stock comes in, a product becomes visible again within the drain window.
The reverse (a product selling out and staying listed a few minutes) is harmless:
the cart and checkout always re-verify real stock, so the shop never oversells.

Known issues / Roadmap
======================

* Products with several variants are out of scope: they are never hidden. This
  matches Odoo's ``_is_sold_out``, which only checks the first variant.
* With Click & Collect (``website_sale_collect``) availability is per visitor and
  cannot be represented on the product, so the filter does not apply.
* ``website_sale_multi_warehouse`` (union of published warehouses) is out of
  scope. The scope derivation and the availability computation are isolated in
  overridable methods so a bridge module can support it without a rewrite.
* Hiding a product removes its "back in stock" notification funnel
  (``stock_notification_partner_ids`` on ``product.product``).

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/ingadhoc/website/issues>`_.

Credits
=======

Authors
~~~~~~~

* ADHOC SA

Maintainer
~~~~~~~~~~

.. image:: https://raw.githubusercontent.com/ingadhoc/maintainer-tools/master/resources/adhoc-logo.png
   :alt: ADHOC SA
   :target: https://www.adhoc.com.ar

This module is maintained by ADHOC SA.
