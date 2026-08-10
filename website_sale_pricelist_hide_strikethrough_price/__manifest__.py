##############################################################################
#
#    Copyright (C) 2026  ADHOC SA  (http://www.adhoc.com.ar)
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
    "name": "Website Sale Pricelist Hide Strikethrough Price",
    "category": "website",
    "version": "19.0.1.0.0",
    "author": "ADHOC SA",
    "website": "www.adhoc.com.ar",
    "license": "AGPL-3",
    "summary": "Hide strikethrough/compare prices in the eCommerce per pricelist",
    "depends": [
        "website_sale",
    ],
    "data": [
        "views/product_pricelist_views.xml",
        "views/website_sale_templates.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "website_sale_pricelist_hide_strikethrough_price/static/src/scss/website_sale_hide_strikethrough.scss",
        ],
    },
    "installable": True,
}
