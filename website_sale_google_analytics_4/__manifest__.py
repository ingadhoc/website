{
    "name": "Google Analytics 4 Ecommerce Tracking",
    "summary": "Server-side GA4 event delivery and the events Odoo does not cover",
    "version": "20.0.1.0.0",
    "author": "ADHOC SA",
    "category": "Website",
    "license": "AGPL-3",
    "depends": ["website_sale", "payment"],
    "data": [
        "data/ir_cron.xml",
        "views/res_config_settings_view.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "website_sale_google_analytics_4/static/src/interactions/ga4_user_tracking.js",
        ],
    },
    "installable": True,
    "application": False,
}
