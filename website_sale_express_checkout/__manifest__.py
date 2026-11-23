##############################################################################
#
#    Copyright (C) 2026  ADHOC SA
#    All Rights Reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    "name": "Website Sale Express Checkout AR",
    "version": "19.0.1.0.0",
    "author": "ADHOC SA",
    "website": "www.adhoc.com.ar",
    "license": "AGPL-3",
    "category": "Website/Website",
    "summary": "One-page checkout for Argentinean eCommerce, with server-side tax derivation",
    "depends": [
        "website_sale",
        "l10n_ar_website_sale",
        "website_sale_background_post",
    ],
    "data": [
        "data/website_checkout_step_data.xml",
        "views/res_config_settings_views.xml",
        "views/express_checkout_templates.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "website_sale_express_checkout/static/src/interactions/express_checkout.js",
        ],
    },
    "post_init_hook": "post_init_hook",
    "uninstall_hook": "uninstall_hook",
    "installable": True,
    "auto_install": False,
    "application": False,
}
