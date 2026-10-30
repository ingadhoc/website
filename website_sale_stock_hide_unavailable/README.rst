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
products per warehouse scope) and the storefront only adds a SQL sub-query to
the domain it already builds. Nothing in the hot request path computes stock.

.. contents::
   :local:

Technical details
=================

* ``product.template.stock.availability``: the precomputed table, keyed by
  ``(product_tmpl_id, warehouse_id, company_id)``. A row means *unavailable*;
  absence means visible, so missing data fails open and a sellable product is
  never hidden by a stale computation. ``warehouse_id`` is empty on the
  company-wide scope, which needs its own partial unique index because Postgres
  does not enforce uniqueness across NULLs.
* ``product.template.stock.dirty``: the queue the recompute drains.
* ``product.template.stock_unavailability_ids`` is declared with
  ``bypass_search_access`` so the ``not any`` sub-query resolves for public and
  portal shoppers without granting them read access to the table, which would
  leak per-warehouse stock over RPC.
* One override of ``website.sale_product_domain()`` covers the listing, the
  site search, the sitemap, the accessory/alternative blocks and the category
  product count at once. The "at the end" order is a stable Python re-sort in
  ``WebsiteSale._shop_lookup_products``, which changes neither the product count
  nor the paging.
* The carousels never call ``sale_product_domain()``, so
  ``website.snippet.filter._prepare_values`` adds the same leaf: it is where the
  two kinds of dynamic filter meet, the one backed by an ``ir.filters`` and the
  one backed by a server action.
* A ``stock.quant`` hook enqueues the touched candidates with a single SQL
  statement, taking no row locks on ``product_template``.
  ``_hide_unavailable_extra_templates`` is the seam a bridge fills with the
  products whose availability is derived from others (see the ``mrp`` bridge).
* Two scheduled actions reconcile the table: a 5-minute drain and a nightly full
  sweep with a resumable cursor, both reusing the standard batched ``free_qty``
  compute, so mrp kits and expiry are respected.
* ``_hide_unavailable_scope_leaf`` and ``_hide_unavailable_free_qty`` are left
  overridable so a multi-warehouse bridge can support the union of published
  warehouses without a rewrite.
* ``_post_init_hook`` removes ``website_sale.group_unpublish_out_of_stock``
  from ``website.group_website_restricted_editor``.

Installation
============

To install this module, you need to:

#. Just install this module.

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
setting is hidden and turned off on install. The native one is a single switch
for the whole database, it overwrites manual publishing, and it unpublishes the
product, so its page stops answering 200.

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

* With Click & Collect (``website_sale_collect``) availability is per visitor and
  cannot be represented on the product, so the filter does not apply.
* ``website_sale_multi_warehouse`` (union of published warehouses) is out of
  scope. The scope derivation and the availability computation are isolated in
  overridable methods so a bridge module can support it without a rewrite.
* Hiding a product removes its "back in stock" notification funnel
  (``product.stock.notification``).
* Kits (``mrp``) need ``website_sale_stock_hide_unavailable_mrp``, which
  installs itself alongside ``mrp``. Without it a kit is only refreshed by the
  nightly sweep, because its availability comes from its components.
* Enabling Odoo's native unpublishing over RPC is still possible: this module
  hides the setting, it does not override ``_compute_is_published``.

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
