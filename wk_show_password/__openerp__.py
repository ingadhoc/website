# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#################################################################################
{
    "name": "Website Show Password",
    "category": 'Website',
    "summary": """
        Option to View Password at Login and Signup page.""",
    "description": """

====================
**Help and Support**
====================
.. |icon_features| image:: wk_show_password/static/src/img/icon-features.png
.. |icon_support| image:: wk_show_password/static/src/img/icon-support.png
.. |icon_help| image:: wk_show_password/static/src/img/icon-help.png

|icon_help| `Help <https://webkul.com/ticket/open.php>`_ |icon_support| `Support <https://webkul.com/ticket/open.php>`_ |icon_features| `Request new Feature(s) <https://webkul.com/ticket/open.php>`_
    """,
    "author": "Webkul Software Pvt. Ltd.",
    "website": "http://www.webkul.com",
    "version": '1.0',
    "depends": ['website_sale'],
    "data": [
        'views/auth_signup_login.xml',
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
    "images":['static/description/Banner.png']
}