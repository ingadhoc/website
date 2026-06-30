##############################################################################
#
#    Copyright (C) 2015  ADHOC SA  (http://www.adhoc.com.ar)
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
    "name": "l10n_ar Website Sale UX",
    "category": "Website/Website",
    "version": "18.0.1.4.0",
    "author": "ADHOC SA",
    "website": "www.adhoc.com.ar",
    "license": "AGPL-3",
    "depends": [
        "website_sale",
        "l10n_ar_website_sale",
    ],
    "data": [
        "views/l10n_ar_website_sale_ux.xml",
        "views/l10n_ar_website_sale_hide_taxes.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "l10n_ar_website_sale_ux/static/src/js/website_sale.js",
        ],
    },
    "installable": True,
    "auto_install": ["l10n_ar_website_sale"],
}
