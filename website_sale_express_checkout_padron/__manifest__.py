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
    "name": "Website Sale Express Checkout AR - ARCA Padron Bridge",
    "version": "19.0.1.0.0",
    "author": "ADHOC SA",
    "website": "www.adhoc.com.ar",
    "license": "AGPL-3",
    "category": "Website/Website",
    "summary": "Fills the Factura A billing partner from the ARCA padron on express checkout",
    "depends": [
        "website_sale_express_checkout",
        "l10n_ar_edi_ux",
    ],
    "data": [],
    "installable": True,
    "auto_install": True,
    "application": False,
}
