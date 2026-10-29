from odoo import api, models


class MrpBom(models.Model):
    _inherit = "mrp.bom"

    @api.model_create_multi
    def create(self, vals_list):
        boms = super().create(vals_list)
        boms._enqueue_hide_unavailable_kits()
        return boms

    def write(self, vals):
        # Before: a bill that stops being a kit must be enqueued too.
        self._enqueue_hide_unavailable_kits()
        res = super().write(vals)
        self._enqueue_hide_unavailable_kits()
        return res

    def unlink(self):
        kits = self._hide_unavailable_kits()
        res = super().unlink()
        kits._enqueue_stock_availability()
        return res

    def _hide_unavailable_kits(self):
        """The candidate templates whose availability comes from these bills."""
        kits = self.filtered(lambda bom: bom.type == "phantom").product_tmpl_id
        return kits.filtered(lambda tmpl: tmpl._hide_unavailable_is_candidate())

    def _enqueue_hide_unavailable_kits(self):
        self._hide_unavailable_kits()._enqueue_stock_availability()


class MrpBomLine(models.Model):
    _inherit = "mrp.bom.line"

    @api.model_create_multi
    def create(self, vals_list):
        lines = super().create(vals_list)
        lines.bom_id._enqueue_hide_unavailable_kits()
        return lines

    def write(self, vals):
        boms = self.bom_id
        res = super().write(vals)
        (boms | self.bom_id)._enqueue_hide_unavailable_kits()
        return res

    def unlink(self):
        boms = self.bom_id
        res = super().unlink()
        boms._enqueue_hide_unavailable_kits()
        return res
