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

Adds a setting to cancel old website quotations automatically.

``sale_ux`` already cancels old backoffice quotations through the *Clean Old
Quotations* scheduled action. Without this module that cleanup does not tell
website quotations apart, so enabling it also cancels the ones placed through
the e-commerce. This module adds a separate switch for the website ones and
makes both switches independent.

Installation
============

To install this module, you need to:

#. Just install this module.

Configuration
=============

To configure this module, you need to:

#. Go to *Settings > Sales*, section *Cancel Old Quotations*, and set after how
   many days a quotation is considered old (field provided by ``sale_ux``).
#. Tick *Sales* to cancel old backoffice quotations, *Website* to cancel old
   e-commerce ones, or both. The *Website* switch is also reachable from
   *Settings > Website*, section *Cancel Old Website Quotations*.

Usage
=====

To use this module, you need to:

#. The daily *Clean Old Quotations* scheduled action, provided by ``sale_ux``,
   cancels every quotation in *Quotation* or *Quotation Sent* state whose order
   date is older than the configured number of days.
#. Which quotations it reaches depends on the two switches: only backoffice
   ones with *Sales*, only e-commerce ones with *Website*, all of them with
   both. With neither one enabled the scheduled action cancels nothing.
#. Each cancelled quotation gets a note in its chatter stating it was cancelled
   automatically because it expired.


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
