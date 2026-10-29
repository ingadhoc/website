from odoo import models


class StockQuant(models.Model):
    _inherit = "stock.quant"

    def _hide_unavailable_extra_templates(self):
        """Add the kits whose components these quants hold.

        free_qty already reports a kit from its components, but the enqueue
        walks quant -> product -> template, so moving a component's stock never
        reached the kit: it stayed listed until the nightly sweep.

        Nested kits are covered by following the components up as long as new
        kits appear, which also ends on a recursive bill of materials.
        """
        templates = super()._hide_unavailable_extra_templates()
        kits = self.env["product.template"]
        components = self.product_id
        while components:
            lines = (
                self.env["mrp.bom.line"]
                .sudo()
                .search([("product_id", "in", components.ids), ("bom_id.type", "=", "phantom")])
            )
            found = lines.bom_id.product_tmpl_id - kits
            if not found:
                break
            kits |= found
            components = found.product_variant_ids
        return templates | kits
