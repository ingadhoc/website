from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    acquirers = env['payment.acquirer'].search([
        ('provider', '=', 'todopago'),
    ])
    acquirers.write({
        'todopago_test_client_id': '2159',
        'todopago_test_secret_key': 'PRISMA A793D307441615AF6AAAD7497A75DE59',
    })
