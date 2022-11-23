.. |company| replace:: ADHOC SA

.. |company_logo| image:: https://raw.githubusercontent.com/ingadhoc/maintainer-tools/master/resources/adhoc-logo.png
   :alt: ADHOC SA
   :target: https://www.adhoc.com.ar

.. |icon| image:: https://raw.githubusercontent.com/ingadhoc/maintainer-tools/master/resources/adhoc-icon.png

.. image:: https://img.shields.io/badge/license-AGPL--3-blue.png
   :target: https://www.gnu.org/licenses/agpl
   :alt: License: AGPL-3

=================================
Unique Description for E-commerce
=================================

By default Odoo has only one field for adding Product description info, which is editable from Product's backend view / Sales / Sale description. This field is displayed on both, the sale bill documents and the ecommerce product page. Because sometimes it is mandatory to display different info texts on those views, e.g. a short description for sale bill documents but a longer one on ecommerce, we have created this module which add an extra editable field on product's backend view called "Website description".

Important: if Website description field is empty but Product description field is filled up then Product description content will be displayed in both, sales bill documents and ecommerce product page. On the other hand, if Website description field is filled up and also Product description is filled up then the Website description content will be displayed on ecommerce product page only, and Product description content will be displayed in sales bill documents only.

Installation
============

To install this module, you need to:

#. Just install.

Configuration
=============

To configure this module, you need to:

#. Nothing to configure.

Usage
=====

To use this module, you need to:

#. Go to a Product template, and you will see in 'eCommerce' tab a 'Description for Website' text field

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
