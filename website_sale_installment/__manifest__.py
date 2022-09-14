{
    'name': 'Website Sale Card Installment',
    'category': 'Website',
    'summary': 'Website Sale',
    'version': "15.0.1.0.0",
    'author': 'ADHOC SA',
    'website': 'www.adhoc.com.ar',
    'license': 'AGPL-3',
    'depends': [
        'website',
        'website_sale',
        'card_installment',
    ],
    'data': [
        'views/templates.xml',
        'views/account_card.xml',
        'views/res_config_setting.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'website_sale_installment/static/src/js/card_installment.js',
        ],
    },
    'installable': True,
    'application': False,
}
