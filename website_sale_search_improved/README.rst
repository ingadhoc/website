.. |company| replace:: ADHOC SA

.. |company_logo| image:: https://raw.githubusercontent.com/ingadhoc/maintainer-tools/master/resources/adhoc-logo.png
   :alt: ADHOC SA
   :target: https://www.adhoc.com.ar

.. |icon| image:: https://raw.githubusercontent.com/ingadhoc/maintainer-tools/master/resources/adhoc-icon.png

.. image:: https://img.shields.io/badge/license-AGPL--3-blue.png
   :target: https://www.gnu.org/licenses/agpl
   :alt: License: AGPL-3

============================
Website Sale Search Improved
============================

This module allows the users to expand the search of the eCommerce's search bar by including new fields in its search. Any stored field of the product.template model, or a path through a one2many or many2many field to a field of the related model (e.g. 'product_tag_ids.name'), can be included in the search results.

Odoo natively searches products by name, internal reference, barcode, attribute values, tags, public categories and descriptions; this module adds the fields you configure on top of those.

Important: when the fuzzy search (results even with typing mistakes) is enabled, which is the default in the shop, non-stored fields are removed from the search, so only stored fields are searched.

Installation
============

To install this module, you need to:

#. Only need to install the module

Configuration
=============

To configure this module, you need to:

Go to Settings > Website > eCommerce and activate the feature "Advanced Search Fields". Then add the list of new fields to be included in the search following this structure: ['field_1','field_2.name'] and click on Save.

Relational fields must point to a field of the related model (e.g. 'product_tag_ids.name'), and the public user must have read access to every model in the path; otherwise the setting is rejected.

Usage
=====

To use this module, you need to:

#. Just Use it.

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
