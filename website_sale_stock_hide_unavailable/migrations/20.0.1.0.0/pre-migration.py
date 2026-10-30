def migrate(cr, version):
    """Drop what the 19.0 shape left behind, before the ORM reshapes the table.

    The table changes key: 19.0 kept (product_tmpl_id, warehouse_id, company_id)
    and 20.0 keeps (product_tmpl_id, website_id). Its rows are a precomputed
    answer the crons derive again, and a missing row means "visible", so
    emptying it hides nothing by mistake. Keeping them would leave every row
    without a website, which is what blocks the NOT NULL of the new column.
    """
    cr.execute("SELECT to_regclass('product_template_stock_availability')")
    if not cr.fetchone()[0]:
        return
    cr.execute("DELETE FROM product_template_stock_availability")
    cr.execute("DROP INDEX IF EXISTS product_template_stock_availability_company_wide_uniq")
