from odoo import api, fields, models
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

    @api.model
    def _create_skip_conflicts(self, vals_list):
        """Insert rows, ignoring those another run already created.

        The drain and the sweep can run at the same time and compute the same
        row; a plain create would raise on the unique constraint and lose the
        whole batch.
        """
        if not vals_list:
            return
        uid = self.env.uid
        rows = SQL(", ").join(
            SQL(
                "(%s, %s, %s, %s, now() at time zone 'UTC', %s, now() at time zone 'UTC')",
                vals["product_tmpl_id"],
                vals.get("warehouse_id") or None,
                vals["company_id"],
                uid,
                uid,
            )
            for vals in vals_list
        )
        self.env.cr.execute(
            SQL(
                """
                INSERT INTO product_template_stock_availability
                    (product_tmpl_id, warehouse_id, company_id,
                     create_uid, create_date, write_uid, write_date)
                VALUES %s
                ON CONFLICT DO NOTHING
                """,
                rows,
            )
        )
        # The raw insert bypasses the ORM, so invalidate both this model and the
        # inverse one2many, which a plain create() would have invalidated too.
        self.invalidate_model()
        self.env["product.template"].invalidate_model(["stock_unavailability_ids"])

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
