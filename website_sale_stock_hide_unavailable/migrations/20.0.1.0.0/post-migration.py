from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    """Take over Odoo's own unpublishing, as the install hook does on a new one.

    post_init_hook only runs on install, so an upgraded database would keep the
    native setting on with no way to see it: the module hides it.
    """
    env = api.Environment(cr, SUPERUSER_ID, {})
    env["website"]._hide_unavailable_take_over_native()
