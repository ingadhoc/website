from odoo import models


class WebsiteSnippetFilter(models.Model):
    _inherit = "website.snippet.filter"

    def _prepare_values(self, limit=None, search_domain=None, **options):
        """Keep hidden products out of the dynamic snippets (the carousels).

        The snippets never go through website.sale_product_domain(), so the
        single override that covers the listing, the search, the sitemap, the
        accessory blocks and the category counts does not reach them. A filter
        backed by an ir.filters searches with its own domain, and one backed by
        a server action ends up in _get_products(), which builds another one.
        Both meet here, so the leaf is added once.

        search_domain stays a list: website_sale reads and pops its
        "hide_variants" marker out of it before the base turns it into a Domain.
        These records are variants, so the leaf crosses through the template.
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
