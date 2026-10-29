from . import models
from . import controllers


def _post_init_hook(env):
    """Turn off Odoo's own out-of-stock unpublishing, which this module replaces.

    Both at once is not an error, but it defeats the purpose: the product page
    stops answering 200 and a single base-wide switch overrides the per-website
    setting. The native setting is hidden from the Settings page, so a database
    that already had it on could not turn it off from the interface.
    """
    group = env.ref("website_sale.group_unpublish_out_of_stock", raise_if_not_found=False)
    editor = env.ref("website.group_website_restricted_editor", raise_if_not_found=False)
    if group and editor:
        editor._remove_group(group.sudo())
