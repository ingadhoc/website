.. |company| replace:: ADHOC SA

.. |company_logo| image:: https://raw.githubusercontent.com/ingadhoc/maintainer-tools/master/resources/adhoc-logo.png
   :alt: ADHOC SA
   :target: https://www.adhoc.com.ar

.. |icon| image:: https://raw.githubusercontent.com/ingadhoc/maintainer-tools/master/resources/adhoc-icon.png

.. image:: https://img.shields.io/badge/license-AGPL--3-blue.png
   :target: https://www.gnu.org/licenses/agpl
   :alt: License: AGPL-3

==============================
Website Sale Installment Plans
==============================

This module shows the card installment plans on the website shop, under the price of each product.

On the product page and in the shop grid, every published installment plan of an active card of the
website company (or of a card without company) is listed with the number of installments, the amount
of each one and the total, in the website currency. On the product page the legend is refreshed when
another variant is selected. Products with a zero or hidden price show no legend.

Installation
============

To install this module, you need to:

#. Just install ...

Configuration
=============

To configure this module, you need to:

#. Go to Accounting > Configuration > Cards and open a card.
#. In its installment plans, check *Published in website* on the plans to show in the shop.
#. Optionally fill *Message*, which is displayed at the end of the plan legend.

Usage
=====

To use this module, you need to:

#. Go to the website shop: each product with a price shows the published installment plans under it.
#. Open a product: the plans are shown under the price and change with the selected variant.


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

.. image:: https://github.com/ingadhoc/website/raw/20.0/website_sale_installment_plans/static/description/feature_img.png

* |company| |icon|

Contributors
------------

Maintainer
----------

|company_logo|

This module is maintained by the |company|.

To contribute to this module, please visit https://www.adhoc.com.ar.
