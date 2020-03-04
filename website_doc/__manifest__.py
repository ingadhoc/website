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
    'name': 'Website Documentation',
    'category': 'Website',
    'summary': 'Website, Documentation',
    'version': '12.0.1.5.0',
    'author': 'ADHOC SA',
    'website': 'www.adhoc.com.ar',
    'license': 'AGPL-3',
    'depends': [
        'base_search_fuzzy',
        'base_name_search_improved',
        'google_drive',
        'website',
    ],
    'external_dependencies': {
        'python': ['html2text']
    },
    'data': [
        'data/doc_data.xml',
        'data/ir_model_data.xml',
        'security/ir.model.access.csv',
        'security/website_doc_security.xml',
        'views/website_doc_toc_views.xml',
        'views/website_doc_toc_templates.xml',
    ],
    'demo': [
    ],
    'installable': False,
    'application': True,
}
