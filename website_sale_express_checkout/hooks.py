##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
EXPRESS_HREF = "/shop/express_checkout"
DELIVERY_HREF = "/shop/checkout"
EXTRA_HREF = "/shop/extra_info"


def post_init_hook(env):
    """Propagate the generic ``express_checkout`` step to every existing website.

    New websites get it through ``website._create_checkout_steps`` (which copies
    every generic step); pre-existing websites need it copied here. Publication
    is then synced from each website's ``enable_express_checkout`` flag, which is
    ``False`` by default -> installing the module leaves the standard flow intact.
    """
    generic_step = env.ref("website_sale_express_checkout.checkout_step_express", raise_if_not_found=False)
    for website in env["website"].search([]):
        if generic_step and not website._get_checkout_step(EXPRESS_HREF):
            generic_step.copy({"website_id": website.id, "is_published": False})
        website._sync_express_checkout_steps()


def uninstall_hook(env):
    """Remove the per-website express step and restore delivery/extra publication."""
    Step = env["website.checkout.step"].sudo()
    for website in env["website"].search([]):
        Step.search(
            [
                ("website_id", "=", website.id),
                ("step_href", "=", EXPRESS_HREF),
            ]
        ).unlink()
        delivery = website._get_checkout_step(DELIVERY_HREF)
        extra = website._get_checkout_step(EXTRA_HREF)
        delivery.is_published = True
        # extra_info follows the view's active state, as core does on step creation
        extra.is_published = website.with_context(website_id=website.id).viewref("website_sale.extra_info").active
