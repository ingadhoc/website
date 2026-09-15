{
    "name": "Website Sale Cart Offcanvas",
    "summary": "Show the cart in a side panel when adding a product or clicking the cart icon",
    "version": "19.0.1.0.0",
    "author": "ADHOC SA",
    "website": "www.adhoc.com.ar",
    "category": "Website",
    "license": "AGPL-3",
    "depends": ["website_sale"],
    "data": [
        "views/templates.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "website_sale_cart_offcanvas/static/src/**/*",
        ],
        "web.assets_tests": [
            "website_sale_cart_offcanvas/static/tests/tours/**/*",
        ],
    },
    "installable": True,
    "application": False,
}
