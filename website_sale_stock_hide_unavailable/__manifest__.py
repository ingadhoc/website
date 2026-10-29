{
    "name": "Website Sale Stock Hide Unavailable",
    "summary": "Hide or push down out-of-stock products in the eCommerce shop",
    "version": "20.0.1.0.0",
    "category": "Website",
    "author": "ADHOC SA",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "website_sale_stock",
    ],
    "data": [
        "security/ir.access.csv",
        "data/ir_cron.xml",
        "views/res_config_settings_views.xml",
    ],
    "post_init_hook": "_post_init_hook",
    "website": "https://github.com/ingadhoc/website",
}
