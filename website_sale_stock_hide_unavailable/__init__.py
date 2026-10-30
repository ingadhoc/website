from . import models
from . import controllers


def _post_init_hook(env):
    """Take over Odoo's own out-of-stock unpublishing, which this module replaces.

    This module ships with the shop, so the native setting is never offered: it
    must not stay on where nobody can see it.
    """
    env["website"]._hide_unavailable_take_over_native()
