{
    "name": "Website Sale Installment Plan",
    "category": "Website/Website",
    "version": "20.0.1.0.0",
    "author": "ADHOC SA",
    "website": "www.adhoc.com.ar",
    "license": "AGPL-3",
    "depends": [
        "website_sale",
        "card_installment",
    ],
    "data": [
        "views/account_card_installment_views.xml",
        "views/website_templates.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "website_sale_installment_plans/static/src/interactions/**/*",
        ],
    },
    "installable": True,
}
