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
    'name': 'Facebook Pixel Tracking',
    'category': 'website',
    'version': "18.0.1.0.0",
    'author': 'ADHOC SA',
    'website': 'www.adhoc.com.ar',
    'license': 'AGPL-3',
    'depends': [
        'website_sale_advanced_tracking',
    ],
    'data': [
        'views/res_config_settings_view.xml',
        'views/website_templates.xml',
    ],
    'assets':{
        'web.assets_frontend': [
            'facebook_pixel_tracking/static/src/js/website_sale_tracking.js',
            'facebook_pixel_tracking/static/src/js/website_user_tracking.js'
        ],
    },
    'installable': True,
}
