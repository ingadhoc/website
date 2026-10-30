===============================================
Website Sale Stock Hide Unavailable - Inventory
===============================================

Bridge between ``website_sale_stock_hide_unavailable`` and Inventory. Installs
itself when both get installed, and on an upgrade when both are already there.
A plain ``-u`` of the core module does not bring it in.

Without Inventory the shop reads the company-wide ``qty_available`` that Odoo
keeps in ``product``, and the core module already follows what moves it:
invoices, sales orders and manual edits. With Inventory, stock moves instead,
and nothing of that reaches those triggers.

This module adds the ``stock.quant`` hook that enqueues the products a stock
move touched, so the shop reflects it within the drain window instead of
waiting for the nightly sweep. It also reconciles the catalogue when the
warehouse of a website changes, which changes every answer for that site.

The availability figure itself needs no bridge: the core module asks
``website._get_product_available_qty()``, which ``website_sale_stock``
overrides to measure against the website's warehouse.

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
