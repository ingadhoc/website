{
    "name": "Website Sale Exception Checkout",
    "summary": "Check sale exceptions on the eCommerce checkout, before the payment",
    "version": "19.0.1.0.0",
    "category": "Website",
    "author": "ADHOC SA",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "auto_install": True,
    "depends": [
        "website_sale",
        "sale_exception",
    ],
    "data": [
        "views/exception_rule_views.xml",
        "views/templates.xml",
    ],
    "website": "https://github.com/ingadhoc/website",
}
