from odoo import fields, models


class ProductTemplateStockDirty(models.Model):
    """Queue of products whose e-commerce availability must be recomputed.

    Filled cheaply (no dedup on insert) by the stock.quant hooks; the drain
    cron deduplicates on read and clears the processed rows.
    """

    _name = "product.template.stock.dirty"
    _description = "E-commerce stock availability recompute queue"

    product_tmpl_id = fields.Many2one("product.template", required=True, index=True, ondelete="cascade")
