from odoo import models, fields, _


class StockWarehouse(models.Model):

    _inherit = 'stock.warehouse'

    website_published = fields.Boolean(
        'Visible in Portal / Website',
        copy=False,
        default=True,
        help="Only published warehouses are going to be used to get stock on "
        "e-commerce"
    )

    def toggle_website_published(self):
        self.ensure_one()
        self.website_published = not self.website_published
        return True
