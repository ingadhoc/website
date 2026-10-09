##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################


def migrate(cr, version):
    """Keep the panel on only where it was on before the upgrade.

    Odoo 20 dropped `website.add_to_cart_action`, which this module used to extend with
    an `open_offcanvas` value. The column still holds the old value at this point, so it
    decides the new switch; without this every site that merely had the module installed
    would come out of the upgrade with the panel turned on.
    """
    cr.execute("""
        SELECT 1 FROM information_schema.columns
         WHERE table_name = 'website' AND column_name = 'add_to_cart_action'
    """)
    if not cr.fetchone():
        return
    cr.execute("""
        UPDATE website
           SET cart_offcanvas_enabled = (add_to_cart_action = 'open_offcanvas')
    """)
