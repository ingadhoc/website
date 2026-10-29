from odoo import models


class StockQuant(models.Model):
    _inherit = "stock.quant"

    def _hide_unavailable_extra_templates(self):
        """Add the kits whose components these quants hold.

        free_qty already derives a kit from its components, but the enqueue
        walks quant -> product -> template and never reached the kit.
        """
        templates = super()._hide_unavailable_extra_templates()
        Line = self.env["mrp.bom.line"].sudo()
        # The enqueue is a hot path: skip the lookup on a base without kits.
        if not self.env["mrp.bom"].sudo().search_count([("type", "=", "phantom")], limit=1):
            return templates
        kits = self.env["product.template"]
        components = self.product_id
        while components:
            lines = Line.search([("product_id", "in", components.ids), ("bom_id.type", "=", "phantom")])
            found = lines.bom_id.product_tmpl_id - kits
            if not found:
                break
            kits |= found
            components = found.product_variant_ids
        return templates | kits
