from odoo import fields, models
from odoo.tools import SQL


class ProductTemplateStockAvailability(models.Model):
    """Precomputed e-commerce unavailability.

    Polarity rule: a row exists only for products that are NOT available in a
    given scope. Absence of a row means the product is visible. Missing data
    therefore fails open: we never hide a sellable product because the cron did
    not run yet.
    """

    _name = "product.template.stock.availability"
    _description = "E-commerce precomputed stock unavailability"

    product_tmpl_id = fields.Many2one("product.template", required=True, index=True, ondelete="cascade")
    warehouse_id = fields.Many2one(
        "stock.warehouse", index=True, help="Empty means the availability is measured over the whole company."
    )
    company_id = fields.Many2one("res.company", required=True, index=True)

    _scope_uniq = models.Constraint(
        "unique(product_tmpl_id, warehouse_id, company_id)",
        "The unavailability of a product is unique per warehouse scope.",
    )

    def init(self):
        # Postgres unique() does not enforce uniqueness across NULLs, so the
        # company-wide rows (warehouse_id IS NULL) need their own partial index.
        self.env.cr.execute(
            SQL("""
            CREATE UNIQUE INDEX IF NOT EXISTS
                product_template_stock_availability_company_wide_uniq
            ON product_template_stock_availability (product_tmpl_id, company_id)
            WHERE warehouse_id IS NULL
        """)
        )
