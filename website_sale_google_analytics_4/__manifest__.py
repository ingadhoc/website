{
    "name": "Google Analytics 4 Ecommerce Tracking",
    "summary": "Server-side and client-side GA4 ecommerce event tracking",
    "version": "19.0.1.0.0",
    "author": "ADHOC SA",
    "category": "Website",
    "license": "AGPL-3",
    "depends": ["website_sale", "payment"],
    "data": [
        "data/ir_cron.xml",
        "views/res_config_settings_view.xml",
        "views/website_sale_templates.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "website_sale_google_analytics_4/static/src/interactions/ga4_ecommerce.js",
            "website_sale_google_analytics_4/static/src/interactions/ga4_user_tracking.js",
        ],
    },
    "installable": True,
    "application": False,
}
