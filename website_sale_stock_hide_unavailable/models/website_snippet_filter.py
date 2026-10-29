from odoo import models


class WebsiteSnippetFilter(models.Model):
    _inherit = "website.snippet.filter"

    def _prepare_values(self, limit=None, search_domain=None, **options):
        """Keep hidden products out of the dynamic snippets (the carousels).

        Both kinds of filter meet here, the ir.filters one and the server-action
        one, so the leaf is added once. search_domain stays a list: website_sale
        pops its "hide_variants" marker out of it.
        """
        website = self.env.website
        # model_name is the computed field that resolves both filter_id and
        # action_server_id; filter_id alone is empty on a server-action filter,
        # which is what website_sale reads here too.
        model_name = self.model_name or options.get("res_model")
        if model_name == "product.product" and website and website.out_of_stock_display == "hide":
            search_domain = [
                *(search_domain or []),
                ("product_tmpl_id.stock_unavailability_ids", "not any", website._hide_unavailable_scope_leaf()),
            ]
        return super()._prepare_values(limit=limit, search_domain=search_domain, **options)
