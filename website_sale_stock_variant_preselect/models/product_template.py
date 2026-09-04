from odoo import models
from odoo.tools import str2bool

PRESELECT_ENABLED_PARAM = "website_sale_stock_variant_preselect.enabled"


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def _get_combination_info(
        self,
        combination=False,
        product_id=False,
        add_qty=1.0,
        uom_id=False,
        only_template=False,
    ):
        """Preselect a variant that has stock instead of the first one in sequence.

        Only acts when our controller asked for it (the product page, see
        `website_sale_preselect_available_variant`) and core would otherwise fall back
        to `_get_first_possible_combination`, i.e. the visitor picked neither attributes
        nor a variant.
        """
        if (
            self.env.context.get("website_sale_preselect_available_variant")
            and not combination
            and not product_id
            and not only_template
        ):
            combination = self._get_first_available_combination()
        return super()._get_combination_info(
            combination=combination,
            product_id=product_id,
            add_qty=add_qty,
            uom_id=uom_id,
            only_template=only_template,
        )

    def _get_first_available_combination(self):
        """Return the first combination, in configured attribute order, whose variant has stock.

        Falls back to `_get_first_possible_combination` (core's behaviour) whenever
        availability says nothing: the kill switch is off, the template is not storable
        or can be sold out of stock, it has a single variant, or no variant has stock.
        """
        self.ensure_one()
        if (
            not self._is_variant_preselect_enabled()
            or not self.is_storable
            or self.allow_out_of_stock_order
            or len(self.product_variant_ids) < 2
        ):
            return self._get_first_possible_combination()

        website = self.env["website"].get_current_website()
        # `free_qty` is computed and not stored: reading it while iterating the recordset
        # keeps the prefetch set, so `_compute_quantities_dict` resolves every variant in a
        # single `_read_group` instead of one query per variant. Going through
        # `_get_product_available_qty` instead of reading `free_qty` here is what keeps the
        # website warehouse -- and the session branch of `website_sale_collect` -- in play.
        available_ids = {
            variant.id for variant in self.product_variant_ids.sudo() if website._get_product_available_qty(variant) > 0
        }
        if not available_ids:
            return self._get_first_possible_combination()

        # `_get_possible_combinations` walks `attribute_line_ids` and their values in the
        # configured order -- the same order the visitor sees in the attribute selector --
        # so the first match is the first available variant as seen from the page.
        for combination in self._get_possible_combinations():
            if self._get_variant_for_combination(combination).id in available_ids:
                return combination
        return self._get_first_possible_combination()

    def _is_variant_preselect_enabled(self):
        """Kill switch, on by default.

        The preselection is not a customer-facing option: it fixes a generic eCommerce
        problem and no shop should have to opt in. The parameter exists so we can turn it
        off on a single database if it ever behaves erratically, without a release.
        """
        return str2bool(
            self.env["ir.config_parameter"].sudo().get_param(PRESELECT_ENABLED_PARAM, "True"),
            True,
        )
