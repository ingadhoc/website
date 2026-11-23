##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import fields, models

EXPRESS_HREF = "/shop/express_checkout"
DELIVERY_HREF = "/shop/checkout"
EXTRA_HREF = "/shop/extra_info"


class Website(models.Model):
    _inherit = "website"

    enable_express_checkout = fields.Boolean(
        string="Express Checkout (AR)",
        help="Collapse the eCommerce checkout into a single page and derive the "
        "Argentinean tax data server-side. Only takes effect when the cart's "
        "company is Argentinean; other companies keep the native flow.",
    )

    def _create_checkout_steps(self):
        # super() copies every generic step (including our express_checkout one)
        # into a per-website record; then we set publication from the flag.
        super()._create_checkout_steps()
        self._sync_express_checkout_steps()

    def write(self, vals):
        res = super().write(vals)
        if "enable_express_checkout" in vals:
            self._sync_express_checkout_steps()
            if vals.get("enable_express_checkout"):
                # Background invoice validation is mandatory: a synchronous ARCA
                # call inside the payment request would break cart confirmation.
                self.company_id.sudo().website_sale_background_post = True
        return res

    def _sync_express_checkout_steps(self):
        """Publish express_checkout and hide delivery/extra (or the inverse)."""
        for website in self:
            express = website._get_checkout_step(EXPRESS_HREF)
            delivery = website._get_checkout_step(DELIVERY_HREF)
            extra = website._get_checkout_step(EXTRA_HREF)
            express.is_published = website.enable_express_checkout
            delivery.is_published = not website.enable_express_checkout
            # The extra-info step follows the view's active state (as core does)
            # in both modes: the express flow routes through it when the merchant
            # enabled it, and skips it otherwise.
            extra.is_published = website.with_context(website_id=website.id).viewref("website_sale.extra_info").active
