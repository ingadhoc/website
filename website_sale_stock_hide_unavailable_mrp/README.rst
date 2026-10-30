=========================================
Website Sale Stock Hide Unavailable - MRP
=========================================

Bridge between ``website_sale_stock_hide_unavailable`` and ``mrp``. Installs
itself when both are present.

A kit (a product with a *phantom* bill of materials) has no stock of its own:
its availability comes from its components. ``free_qty`` already reports that
correctly, but the queue that keeps the precomputed table fresh walks from the
stock move to the product it is on, so moving a component's stock never
reached the kit. The kit stayed listed in the shop until the nightly sweep.

This module adds those kits to the queue, following nested bills of materials
as deep as they go.

Nothing to configure: the behaviour follows the **Out-of-Stock Products**
setting of each website, in the module it extends.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/ingadhoc/website/issues>`_.

Credits
=======

Authors
~~~~~~~

* ADHOC SA
