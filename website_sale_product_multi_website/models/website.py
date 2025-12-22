from odoo import models
from odoo.orm.domains import Domain


class Website(models.Model):
    _inherit = "website"

    def website_domain(self):
        self.ensure_one()
        if self.env.context.get("multi_website_domain"):
            return Domain("website_ids", "=", False) | Domain("website_ids", "in", self.ids)
        return super().website_domain()

    def sale_product_domain(self):
        """We add a context in order to change the way that website_domain behaves"""
        return super(Website, self.with_context(multi_website_domain=True)).sale_product_domain()
