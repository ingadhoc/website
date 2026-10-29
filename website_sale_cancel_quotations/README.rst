.. |company| replace:: ADHOC SA

.. |company_logo| image:: https://raw.githubusercontent.com/ingadhoc/maintainer-tools/master/resources/adhoc-logo.png
   :alt: ADHOC SA
   :target: https://www.adhoc.com.ar

.. |icon| image:: https://raw.githubusercontent.com/ingadhoc/maintainer-tools/master/resources/adhoc-icon.png

.. image:: https://img.shields.io/badge/license-AGPL--3-blue.png
   :target: https://www.gnu.org/licenses/agpl
   :alt: License: AGPL-3

==============================
Website Sale Cancel Quotations
==============================

Add a setting for automatic cancellation of website quotations.

Installation
============

To install this module, you need to:

#. Just install this module.

Configuration
=============

To configure this module, you need to:

#. Go to Settings > Website and, in the eCommerce block, turn on Website under
   Cancel Old Quotations. The same setting is also available in
   Settings > Sales, next to the one that covers back office quotations.
#. The setting is common to all websites: the website selector at the top of
   the page does not scope it, so turning it on from one website turns it on
   for every one.
#. Set how many days a quotation is kept in Cancel quotations older than. This
   number is shared with Sales and defaults to 30 days.

Usage
=====

To use this module, you need to:

#. Once the setting is on, the daily Clean Old Quotations scheduled action
   cancels every order of the website that is older than the configured number
   of days and still in Quotation or Quotation Sent. Confirmed orders are never
   cancelled, and each cancellation is logged in the chatter of the order.
#. Mind that an abandoned cart is one of those orders: it is a quotation with a
   website, and the action has no way of telling the two apart. Turning the
   setting on therefore cancels the backlog of abandoned carts as well, which on
   a busy shop is most of what it finds.
#. The two settings are independent: with only Website on, back office
   quotations are left alone; with only Sales on, website quotations are left
   alone.


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
