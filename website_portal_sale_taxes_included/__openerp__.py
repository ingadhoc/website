# -*- coding: utf-8 -*-
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
    'name': 'Website Portal for Sales With Taxes Included or Not',
    'version': '9.0.1.0.0',
    'category': 'Product',
    'sequence': 14,
    'summary': '',
    'description': '''
Website Portal for Sales With Taxes Included
============================================
    ''',
    'author':  'ADHOC SA',
    'website': 'www.adhoc.com.ar',
    'license': 'AGPL-3',
    'images': [
    ],
    'depends': [
        'website_portal_sale',
        # TODO tenemos que mejorar o separar integracion entre
        # l10n_ar_invoice_sale y product_price_taxes_included
        'l10n_ar_invoice_sale',
        # 'product_price_taxes_included',
    ],
    'data': [
        'views/templates.xml',
        # 'security/ir.model.access.csv',
    ],
    'demo': [
    ],
    'test': [
    ],
    'installable': False,
    'auto_install': False,
    'application': False,
}
