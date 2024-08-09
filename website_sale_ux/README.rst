.. |company| replace:: ADHOC SA

.. |company_logo| image:: https://raw.githubusercontent.com/ingadhoc/maintainer-tools/master/resources/adhoc-logo.png
   :alt: ADHOC SA
   :target: https://www.adhoc.com.ar

.. |icon| image:: https://raw.githubusercontent.com/ingadhoc/maintainer-tools/master/resources/adhoc-icon.png

.. image:: https://img.shields.io/badge/license-AGPL--3-blue.png
   :target: https://www.gnu.org/licenses/agpl
   :alt: License: AGPL-3

===============
Website Sale UX
===============

#. This module adds the option to "Search Website Product Category for" (public_categ_ids) on Website app`s backend search bar (Website > Product).
#. This module also changes the functionality of the Catalog page`s "Add to cart" buttons (frontend):
    * If the product has not variants, when user clicks Add to cart button then the product is added to the Cart (default behaviour).
    * If the product has variants, when users click the Add to cart button then they are redirected to the Product page (new feature) so they could choice among all variants, instead of opening the pop-up to choice among all variants (default behaviour). This new feature is required because "variant pop-up" shows a malfunction when user tries to add to cart a bigger quantity of a variant product than stock available.
#. Rename "All products" to "All categories" in categories left snippet on shop
#. Add an option to disable returning categories on shop search bar. To do so you need to go to website settings and check option "Disable Categories Search"
#. Add a button on the filters sidebar on ecommerce to get back to the shop page unapplying all filters previously set
#. Makes the native fields description_ecommerce and website_description visible on product.template backend view
#. A toggle button is added on website Builder for 'Product page' cutomization, called "Sale description". This button shows/hides the sale_description field on frontend view

Installation
============

To install this module, you need to:

#. Just install this module.

Configuration
=============

To configure this module, you need to:

#. No configuration needed.

Usage
=====

To use this module, you need to:

#. Just use the module.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: http://runbot.adhoc.com.ar/

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
