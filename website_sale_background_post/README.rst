.. |company| replace:: ADHOC SA

.. |company_logo| image:: https://raw.githubusercontent.com/ingadhoc/maintainer-tools/master/resources/adhoc-logo.png
   :alt: ADHOC SA
   :target: https://www.adhoc.com.ar

.. |icon| image:: https://raw.githubusercontent.com/ingadhoc/maintainer-tools/master/resources/adhoc-icon.png

.. image:: https://img.shields.io/badge/license-AGPL--3-blue.png
   :target: https://www.gnu.org/licenses/agpl
   :alt: License: AGPL-3

============================
Website Sale Background Post
============================

This module lets the invoices of eCommerce orders be validated in background, so an error while validating an invoice (for example, an ARCA error) does not block the cart confirmation.

When the option is enabled for the company and a payment of an order made on the website is confirmed:

#. The invoice is created as usual by the automatic invoicing of eCommerce, but it is not validated at that moment.
#. Customer invoices are left in draft and marked to be posted in background (feature of the module Account Background Post).
#. The background post cron is triggered, so the invoice is validated a moment later.

Payments of orders that do not come from the website, or of companies without the option, are processed as before.

Installation
============

To install this module, you need to:

#. Only need to install the module

Configuration
=============

To configure this module, you need to:

#. Go to Website > Configuration > Settings.
#. Enable Automatic Invoicing.
#. Enable Validate Website Invoices in Background. The option is per company and is only shown when Automatic Invoicing is enabled.

Usage
=====

To use this module, you need to:

#. Nothing to do: once configured, the invoices of the paid website orders are validated by the background post cron.

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
