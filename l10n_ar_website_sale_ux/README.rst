.. |company| replace:: ADHOC SA

.. |company_logo| image:: https://raw.githubusercontent.com/ingadhoc/maintainer-tools/master/resources/adhoc-logo.png
   :alt: ADHOC SA
   :target: https://www.adhoc.com.ar

.. |icon| image:: https://raw.githubusercontent.com/ingadhoc/maintainer-tools/master/resources/adhoc-icon.png

.. image:: https://img.shields.io/badge/license-AGPL--3-blue.png
   :target: https://www.gnu.org/licenses/agpl
   :alt: License: AGPL-3

===========================
Argentinian Website Sale UX
===========================

This module enhances the eCommerce frontend for the Argentinian localization with improved tax indication displays and UX improvements.

Features
========

Enhanced Tax Indication Display
-------------------------------

* **Dynamic Tax Names**: Replaces generic "(Tax excluded)" and "(Tax included)" text with the actual tax name (e.g., "(+ VAT 21% Excluded)" or "(VAT 21% Included)")
* **VAT Only**: Only the VAT taxes of the product are shown (taxes whose tax group has an AFIP VAT code), already mapped by the customer's fiscal position. Other taxes, like internal taxes, are not shown
* **Multi-Context Support**: Works consistently across:

  * Shop page (product grid)
  * Product detail pages

B2B/B2C Tax Display Logic
-------------------------

* **B2B Mode** (tax_excluded): Shows "(+ [Tax Name] Excluded)" next to prices
* **B2C Mode** (tax_included): Shows "([Tax Name] Included)" next to prices
* The mode comes from the "eCommerce Price Display" of the customer's pricelist and, when the pricelist does not set it, from the website configuration
* No tax indication is shown for products without VAT, for products whose price is hidden, or for combo products that show "Taxes calculated at checkout."
* Websites of non-Argentinian companies keep the standard "(Tax excluded)" and "(Tax included)" text

Installation
============

1. Install the module from the Apps menu
2. Enable the "Tax Indication" option of the product page in the website editor

Configuration
=============

The tax indication is shown only when the "Tax Indication" option of the product page is enabled in the website editor. The module then:

* Uses the tax display of the customer's pricelist or, when it is not set, of the website (B2B/B2C)
* Identifies the VAT taxes of each product, mapped by the customer's fiscal position
* Displays the tax names next to the price on the shop and product pages

Dependencies
============

* ``website_sale``: Core eCommerce functionality
* ``l10n_ar_website_sale``: Argentinian website sale localization

Usage
=====

Once installed, the enhanced tax indications will automatically appear throughout your eCommerce site:

1. **Shop Pages**: Enhanced tax information next to product prices
2. **Product Pages**: Detailed tax indication on product detail view

The module respects your website's tax configuration and automatically adjusts the display format accordingly.

Known Issues
============

* Tax information is only displayed for products with VAT taxes
* Requires Argentinian localization (``l10n_ar``) to function properly

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

Contributors
------------

* Your Name <your.email@example.com>

Maintainer
----------

|company_logo|

This module is maintained by |company|.

To contribute to this module, please visit https://www.adhoc.com.ar.
