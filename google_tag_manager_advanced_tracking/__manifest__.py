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
    "name": "Google Tag Manager Advanced Tracking",
    "category": "Website",
    "version": "19.0.1.1.0",
    "author": "ADHOC SA",
    "website": "www.adhoc.com.ar",
    "license": "AGPL-3",
    "depends": [
        "website",
        "website_google_tag_manager",
        "website_sale_advanced_tracking",
    ],
<<<<<<< 09d5c13748170de4e74b6478395abdb1d583a484
    "data": [],
||||||| 45ed18e46a1da84aaa581c3c7ddd9f8587e0ae94
    "data": ["views/snippets.xml"],
=======
    "data": [
        "views/snippets.xml",
        "views/res_config_settings_view.xml",
    ],
>>>>>>> 1c5f85bd58c5be5fddcfdd7168c89249d05cace1
    "assets": {
        "web.assets_frontend": [
            "google_tag_manager_advanced_tracking/static/src/**/*.js",
        ],
    },
    "installable": True,
}
