.. |company| replace:: ADHOC SA

.. |company_logo| image:: https://raw.githubusercontent.com/ingadhoc/maintainer-tools/master/resources/adhoc-logo.png
   :alt: ADHOC SA
   :target: https://www.adhoc.com.ar

.. |icon| image:: https://raw.githubusercontent.com/ingadhoc/maintainer-tools/master/resources/adhoc-icon.png

.. image:: https://img.shields.io/badge/license-AGPL--3-blue.png
   :target: https://www.gnu.org/licenses/agpl
   :alt: License: AGPL-3

===================================================
Website Sale Pricelist Hide Strikethrough Price
===================================================

Hide the strikethrough and compare-at prices of the eCommerce for the customers
of a given pricelist.

Features
========

Per-pricelist setting
---------------------

* Adds the **Hide strikethrough prices** checkbox to the pricelist form, in the
  *Ecommerce* tab, next to *Selectable*.
* The setting applies to every visitor whose active pricelist has it enabled.
  Other pricelists keep showing the prices as usual.

What gets hidden
----------------

* The **discount strikethrough**: the original price that the shop crosses out
  when a pricelist rule lowers it, both on the ``/shop`` grid and on the
  product page.
* The automatic **"Sale" ribbon**, which the shop derives from that same value.
* The **compare-at price** set by hand on the product (*Comparison price*).
* The strikethrough of the **product and combo configurator** dialog.
* The strikethrough of the **cart lines**, through the hook and, as a net, a
  CSS class on the page wrapper.

Installation
============

No special steps. Installing the module adds the field to the pricelist form;
nothing changes until the checkbox is enabled on a pricelist.

Configuration
=============

#. Enable **Pricelists** in *Website > Configuration > Settings*.
#. Open *Website > eCommerce > Pricelists* and pick a pricelist.
#. In the **Ecommerce** tab, tick **Hide strikethrough prices**.

Dependencies
============

* ``website_sale``

Usage
=====

Visitors whose active pricelist has the checkbox enabled see a single price
everywhere in the shop: the one they pay. The prices themselves do not change,
only the reference prices that would reveal the discount.

Known Issues
============

* With the checkbox enabled, the products of that pricelist are left out of the
  **On sale** filter of the shop, which Odoo 20.0 builds from the same value
  that draws the strikethrough. The filter is not offered, but a visitor who
  reaches ``/shop?on_sale=1`` directly sees it with an empty grid.
* Two selectors of the CSS net target a QWeb ``<t>`` element, which renders
  nothing, so they never match. The shop grid is covered by the server-side
  hook anyway.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/ingadhoc/website/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smash it by providing a detailed and welcomed feedback.

Credits
=======

Authors
-------

* |company|

Maintainer
----------

|company_logo|

This module is maintained by |company|.

To contribute to this module, please visit https://www.adhoc.com.ar.
