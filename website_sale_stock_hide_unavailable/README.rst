====================================
Website Sale Stock Hide Unavailable
====================================

Let each website decide what the shop does with storable products that are out
of stock and cannot be sold out of stock: show them (Odoo's default), push them
to the end of the listing, or hide them from the listing, the site search, the
sitemap, the accessory/alternative blocks, the homepage carousels and the
per-category product count.

The product page always keeps responding 200, so indexed URLs and SEO are not
lost during a temporary stock break.

Availability is precomputed in the backend (a small table of *unavailable*
products per website) and the storefront only adds a SQL sub-query to the
domain it already builds. Nothing in the hot request path computes stock.

It ships with the shop: it installs itself along with ``website_sale`` and
works both with and without Inventory. Without it, availability is the
company-wide ``qty_available`` that Odoo 20 keeps in ``product`` and moves with
invoices and sales orders; with Inventory, it is the stock of the website's
warehouse. The module does not resolve that difference itself — it asks
``website._get_product_available_qty()``, the same seam the storefront reads.

.. contents::
   :local:

Technical details
=================

* ``product.template.stock.availability``: the precomputed table, keyed by
  ``(product_tmpl_id, website_id)``. A row means *unavailable*; absence means
  visible, so missing data fails open and a sellable product is never hidden by
  a stale computation. The scope is the website and not the warehouse because
  the website is what knows how availability is measured, with or without
  Inventory.
* ``product.template.stock.dirty``: the queue the recompute drains.
* ``product.template.stock_unavailability_ids`` is declared with
  ``bypass_search_access`` so the ``not any`` sub-query resolves for public and
  portal shoppers without granting them read access to the table, which would
  leak what is sold out over RPC.
* One override of ``website.sale_product_domain()`` covers the listing, the
  site search, the sitemap, the accessory/alternative blocks and the category
  product count at once. The "at the end" order is a stable Python re-sort in
  ``WebsiteSale._shop_lookup_products``, which changes neither the product count
  nor the paging.
* The carousels never call ``sale_product_domain()``, so
  ``website.snippet.filter._prepare_values`` adds the same leaf: it is where the
  two kinds of dynamic filter meet, the one backed by an ``ir.filters`` and the
  one backed by a server action.
* What enqueues a product depends on what moves its stock. In the core module:
  ``qty_available`` changing on the variant — which is also how an invoice moves
  it, through ``account.move._update_qty_available`` — and a sales order
  being confirmed, cancelled, or having its lines changed, which is what moves
  the outgoing quantity ``free_qty`` subtracts. With Inventory, the
  ``..._stock`` bridge adds a ``stock.quant`` hook that enqueues the touched
  candidates with a single SQL statement, taking no row locks on
  ``product_template``; ``_hide_unavailable_extra_templates`` is the seam a
  further bridge fills with products whose availability is derived from others
  (see the ``mrp`` one).
* Two scheduled actions reconcile the table: a 5-minute drain and a nightly full
  sweep with a resumable cursor, both reading availability through
  ``website._get_product_available_qty()``, the same seam the storefront uses,
  so mrp kits are respected.
* One row and one availability pass per website. Several websites of the same
  company and warehouse answer the same and are still computed and stored once
  each: the website is the unit that knows how it measures, and keeping it that
  way is what lets a bridge change the answer per site.
* ``_hide_unavailable_free_qty`` is left overridable so a bridge can change how
  a website measures -- the union of published warehouses, for instance --
  without a rewrite. The row stays keyed by website, so the answer is per site
  either way.
* Nothing is queued and the nightly sweep walks nothing while every website is
  on **Show**. The module ships with the shop, so most databases never turn it
  on, and they must not pay for it.
* ``_post_init_hook`` removes ``website_sale.group_unpublish_out_of_stock``
  from ``website.group_website_restricted_editor``, and the upgrade script of
  20.0.1.0.0 does the same on a database that already had the module. It first
  republishes the products the native setting had already unpublished: with the
  group gone its compute stops running, so they would stay unpublished for
  good, and their publish date is put back so the shop's "Newest Arrivals" does
  not change. Nothing keeps checking afterwards: Odoo's settings page reads the
  group before saving and writes back what it read, so a module undoing it
  mid-save gets undone in turn, and would break the native feature for whoever
  does turn it back on.

Installation
============

Nothing to do on a database that installs **eCommerce** (``website_sale``) from
now on: ``auto_install`` brings this module along with it, and the ``..._stock``
and ``..._mrp`` bridges along with Inventory and Manufacturing.

A database that already had eCommerce is a different matter: ``auto_install``
only fires while a dependency is being installed, and the upgrade's auto
discovery only triggers it for modules the database has never seen. Installing
it there is a decision of the upgrade scripts, not of this module.

Configuration
=============

Go to *Website ‣ Configuration ‣ Settings*, pick a website and set **Out-of-Stock
Products**:

* **Show** (default): identical to standard Odoo.
* **Show at the end of the list**: out-of-stock products appear last, in any sort
  order, still listed in search and sitemap.
* **Hide**: out-of-stock products disappear from listing, search, sitemap,
  accessories/alternatives, carousels and category counts.

A product is a candidate to be hidden or pushed down only when it is published,
storable and has "Sell when Out-of-Stock" disabled. A product with several
variants is hidden when every variant is out of stock, which is the same rule
Odoo uses for its out-of-stock ribbon.

This module replaces Odoo's own **Unpublish out-of-stock products**, so that
setting is never offered while this one is installed, and it is turned off on
install and whenever the setting is saved. The native one is a single switch
for the whole database, it overwrites manual publishing, and it unpublishes the
product, so its page stops answering 200.

Each website answers on its own. With Inventory, the figure follows the
website's **Warehouse** setting — a specific warehouse, or the whole company
when left empty.

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

* With Click & Collect (``website_sale_collect``) the filter does apply, and it
  measures the way Click & Collect does: both read
  ``website._get_product_available_qty()``, which that module overrides. The
  combination has not been tested end to end.
* ``website_sale_multi_warehouse`` (union of published warehouses) is out of
  scope. The scope derivation and the availability computation are isolated in
  overridable methods so a bridge module can support it without a rewrite.
* Hiding a product removes its "back in stock" notification funnel
  (``product.stock.notification``).
* **Hide** also drops the product from the product feed (Google Merchant
  Center), which builds its domain on ``sale_product_domain()``.
* Stock moves need ``website_sale_stock_hide_unavailable_stock`` and kits need
  ``website_sale_stock_hide_unavailable_mrp``. Both are new modules, so they
  install themselves wherever their dependencies are already installed: on a
  fresh install of Inventory or Manufacturing, and on the upgrade that first
  brings them to a database. A plain ``-u`` of this module does not. Without
  them, those products are only refreshed by the nightly sweep.
* Enabling Odoo's native unpublishing over RPC is still possible: this module
  hides the setting, it does not override ``_compute_is_published``.
* Taking over from the native setting republishes every unpublished storable
  product that is sold out, because nothing records which ones it took down. A
  product deliberately unpublished while sitting at zero stock is republished
  with them -- the native one was going to do the same as soon as it had stock.

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
