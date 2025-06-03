.. |company| replace:: ADHOC SA

.. |company_logo| image:: https://raw.githubusercontent.com/ingadhoc/maintainer-tools/master/resources/adhoc-logo.png
   :alt: ADHOC SA
   :target: https://www.adhoc.com.ar

.. |icon| image:: https://raw.githubusercontent.com/ingadhoc/maintainer-tools/master/resources/adhoc-icon.png

.. image:: https://img.shields.io/badge/license-AGPL--3-blue.png
   :target: https://www.gnu.org/licenses/agpl
   :alt: License: AGPL-3

=======================
Website Sale Stock UX
=======================

This module enhances the user experience (UX) in Odoo's website shop by visually indicating out-of-stock products.

Summary
=======

#. Adds a ribbon for out-of-stock products on the website shop and product cards.
#. Optionally blurs product images when items are out of stock and cannot be ordered.
#. Provides a snippet option to enable or disable the out-of-stock ribbon from the website builder.
#. Adds itemprop="availability" for Google Merchant integration, improving SEO and Google Shopping compatibility.

Features
========

#. **Out of Stock Ribbon:** Visibly marks products that are out of stock and not available for ordering with a distinctive ribbon on the product card.
#. **Image Blur:** Optionally blurs the image of products that are out of stock and cannot be purchased.
#. **Website Builder Options:** Adds a checkbox in the website builder to toggle the display of the out-of-stock ribbon.
#. **Google Merchant Integration:** Adds the `itemprop="availability"` attribute to product cards, enabling better integration with Google Merchant and search engines.

Usage
=====

1. When products are out of stock and cannot be ordered, a ribbon and image blur are automatically applied in the shop.
2. Website editors can enable or disable the "Out of stock Ribbon" via the website builder snippet options.

Installation
============

This module depends on `website_sale_stock`.

To install, add the module to your Odoo addons path and update the app list. Then install it from the Apps menu.

Configuration
=============

No additional configuration required. The feature is available immediately after installation.

Technical Details
=================

#. XML templates inherit the main product card template to insert the out-of-stock ribbon and blur effect conditionally.
#. Adds a snippet option for toggling this feature via the website builder.
#. Adds the `itemprop="availability"` attribute to product cards for Google Merchant integration.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/ingadhoc/website/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed feedback.

Credits
=======

#. **Author:** ADHOC SA (http://www.adhoc.com.ar)

Images
------

* |company| |icon|

Maintainer
----------

|company_logo|

This module is maintained by the |company|.

To contribute to this module, please visit https://www.adhoc.com.ar.
