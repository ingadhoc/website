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
#. By default the frontend eCommerce search bar searches among all products when user is on Catalog page and browsing All products category, but if user is browsing an specific product category then the search bar searchs among this category`s products only. This module improves the searching of frontend eCommerce search bar by allowing the users all the time to search among all products no matter which product category is browsing at that moment. This function works when user press enter but not with dropdown pre-search results.
#. By default, on Settings > Website the option Customer account (which set Free sign up option or By invitation on website) is not able. This module adds this setting option per website.

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
