from odoo import models


class ProductRibbon(models.Model):
    _inherit = "product.ribbon"

    def _is_applicable_for(self, product, price_data):
        """Judge the out-of-stock ribbon on the whole template, not on a single variant.

        `website_sale_stock` answers it with `product._is_sold_out()` on the one variant
        the shop grid picked with `_get_first_possible_variant_id`
        (`website_sale/controllers/main.py:470`), which walks the configured attribute
        order and never looks at stock -- the same blind spot this module fixes on the
        product page. On a template whose first variant is sold out, the card is labelled
        "Out of stock" while the page it links to opens on a variant that does have stock.

        This override only ever *removes* the ribbon, never adds one: when some variant
        can still be sold we answer False, and otherwise we defer to `super()`. That way
        the label stays correct when the whole template is sold out, and the exclusions
        other modules declare here -- rental products in `website_sale_stock_renting`,
        for one -- keep working.
        """
        self.ensure_one()
        if self.assign == "out_of_stock" and product:
            template = product.product_tmpl_id
            # Cheap guards first: on a template that is not storable, that can be sold
            # out of stock, or that has a single variant, core already answers correctly
            # and there is nothing to compute.
            if (
                template._is_variant_preselect_enabled()
                and template.is_storable
                and not template.allow_out_of_stock_order
                and len(template.product_variant_ids) > 1
                and template._has_any_variant_available()
            ):
                return False
        return super()._is_applicable_for(product, price_data)
