from odoo import api, models
from odoo.tools import SQL

QUANT_AVAILABILITY_FIELDS = {"quantity", "reserved_quantity", "location_id"}


class StockQuant(models.Model):
    _inherit = "stock.quant"

    @api.model_create_multi
    def create(self, vals_list):
        quants = super().create(vals_list)
        quants._enqueue_website_availability()
        return quants

    def write(self, vals):
        res = super().write(vals)
        if QUANT_AVAILABILITY_FIELDS & vals.keys():
            self._enqueue_website_availability()
        return res

    def _enqueue_website_availability(self):
        """Enqueue the candidate templates touched by these quants.

        A single SQL statement: it discards non-candidates in the same SELECT
        using stored columns, takes no row locks on product_template (SELECT,
        not UPDATE), and writes only to the queue table.
        """
        if not self.ids:
            return
        self.env.cr.execute(
            SQL(
                """
            INSERT INTO product_template_stock_dirty
                (product_tmpl_id, create_uid, create_date, write_uid, write_date)
            SELECT DISTINCT pp.product_tmpl_id, %s, now() at time zone 'UTC',
                            %s, now() at time zone 'UTC'
              FROM stock_quant sq
              JOIN product_product pp ON pp.id = sq.product_id
              JOIN product_template pt ON pt.id = pp.product_tmpl_id
             WHERE sq.id IN %s
               AND pt.is_storable
               AND NOT COALESCE(pt.allow_out_of_stock_order, TRUE)
               AND COALESCE(pt.is_published, FALSE)
            """,
                self.env.uid,
                self.env.uid,
                tuple(self.ids),
            )
        )
