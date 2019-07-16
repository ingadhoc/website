##############################################################################
#
#    Copyright (C) 2015  Moldeo Interactive and ADHOC SA
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
    'name': 'TodoPago Payment Acquirer',
    'category': 'Hidden',
    'summary': 'Payment Acquirer: TodoPago Implementation',
    'version': '12.0.1.0.0',
    'author': 'Moldeo Interactive - www.moldeo.coop,ADHOC SA',
    'website': 'www.adhoc.com.ar',
    'license': 'AGPL-3',
    'depends': [
        'payment',
        # agregamos sale para poder definir el máximo de cuotas
        'sale',
    ],
    'images': [
    ],
    'external_dependencies': {
        'python': [
            'suds',   # TODO K: If we put suds-jurko fail do not know why
            'requests',
            ]
    },
    'data': [
        'views/todopago_templates.xml',
        'views/payment_acquirer_views.xml',
        'views/payment_transaction_views.xml',
        'views/sale_order_views.xml',
        'data/payment_acquirer_data.xml',
    ],
    'demo': [
    ],
    'installable': False,
    'post_init_hook': 'create_missing_journal_for_acquirers',
}
