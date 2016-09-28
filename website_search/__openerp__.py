# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenSur
#    Copyright (C) 2014-Today OpenSur SA (<http://www.opensur.com>).
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
    'name': 'Website Search',
    'category': 'Website',
    'summary': 'Website search',
    'version': '9.0.1.0.0',
    'description': """
Search website content: including pages, blogs posts, blog post comments, customers, job opportunities and products
        """,
    'author': 'OpenSur SA',
    'website': 'https://www.opensur.com',
    'depends': [
        'website'
    ],
    'data': [
        'views/website_search.xml'
    ],
    'qweb': [
        'static/src/xml/*.xml'
    ],
    'demo': [
    ],
    'installable': False,
    'application': True,
}
