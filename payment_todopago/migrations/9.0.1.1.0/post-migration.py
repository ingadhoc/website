from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(cr, version):
    # because this module is renamed, we need to inforce load of this data
    openupgrade.load_data(
        cr, 'payment_todopago', 'views/todopago_view.xml')
