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
#. Rename "All products" to "All categories" in categories left snippet on shop.
#. Adds an option to disable returning categories on shop search bar. To do so you need to go to website settings and check option "Disable Categories Search".
#. Adds a button on the filters sidebar on ecommerce to get back to the shop page unapplying all filters previously set
#. Makes the native fields description_ecommerce and website_description visible on product.template backend view
#. Adds a toggle button on website Builder for 'Products list page' customization, called "Prod. Internal. Ref.". This button shows/hides the product internal reference (default_code) on frontend shop views.
#. Adds a toggle "eCommerce Desc." on the "Products Design" panel of the website Builder, which shows/hides the eCommerce description (description_ecommerce) on the product tiles of the shop, of the wishlist page and of the "Products" dynamic snippet. Natively the shop only offers the quotation description (description_sale), while the product page only shows the eCommerce one, so both can now be shown together, either of them or none. Core's own toggle is renamed from "Description" to "Quotation Desc." to tell them apart. Being an html field, the eCommerce description is clamped to 3 lines on the tile.

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
