from odoo import api, models
from odoo.fields import Domain


class Website(models.Model):
    _inherit = "website"

    @api.model
    def website_domain(self, website_id=False):
        if self.env.context.get("multi_website_domain"):
            return Domain(
                [
                    "|",
                    ("website_ids", "=", False),
                    ("website_ids", "in", [website_id or self.id]),
                ]
            )
        return super().website_domain()

    def sale_product_domain(self):
        """We add a context in order to change the way that website_domain behaves"""
        return super(Website, self.with_context(multi_website_domain=True)).sale_product_domain()
