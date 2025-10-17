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
* **Context-Aware Display**: Automatically detects and displays the specific tax applied to each product
* **Multi-Context Support**: Works consistently across:

  * Shop page (list and grid views)
  * Product detail pages
  * Checkout pages

B2B/B2C Tax Display Logic
-------------------------

* **B2B Mode** (tax_excluded): Shows "(+ [Tax Name] Excluded)" next to prices
* **B2C Mode** (tax_included): Shows "([Tax Name] Included)" next to prices
* **Fallback Support**: Gracefully falls back to generic "VAT excluded/included" when no specific tax is found

Installation
============

1. Install the module from the Apps menu
2. The enhancements are automatically applied to your eCommerce website
3. No additional configuration required

Configuration
=============

No specific configuration is needed. The module automatically:

* Detects the website's tax display preference (B2B/B2C)
* Identifies applicable taxes for each product
* Displays appropriate tax information based on context

Dependencies
============

* ``website_sale``: Core eCommerce functionality
* ``l10n_ar_website_sale``: Argentinian website sale localization

Usage
=====

Once installed, the enhanced tax indications will automatically appear throughout your eCommerce site:

1. **Shop Pages**: Enhanced tax information next to product prices
2. **Product Pages**: Detailed tax indication on product detail view
3. **Checkout**: Consistent tax display during purchase process

The module respects your website's tax configuration and automatically adjusts the display format accordingly.

Known Issues
============

* Tax information is only displayed for products with configured taxes
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
