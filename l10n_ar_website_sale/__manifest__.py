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
    'name': 'e-Commerce Argentina Partner Document',
    'version': '12.0.1.1.0',
    'author': 'ADHOC SA',
    'website': 'www.adhoc.com.ar',
    'license': 'AGPL-3',
    'category': 'Accounting & Finance',
    'data': [
        'views/l10n_ar_website_sale_templates.xml',
        'data/formbuilder_whitelist_data.xml',
        'data/ir_config_parameter_data.xml',
        'wizards/res_config_settings_views.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [],
    'depends': [
        'website_sale',
        'l10n_ar_account',
        'l10n_ar_sale',
        'product_price_taxes_included',
    ],
    'installable': False,
}
