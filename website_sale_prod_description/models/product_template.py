##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import fields, models, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    description_website = fields.Text(
        'Description for Website',
        translate=True,
        help="A description of the Product that you want to communicate on the"
        " ecommerce to your customers. This description will not be used on "
        "Sales Orders, Deliveries and Invoices"
    )

    @api.model
    def _search_get_detail(self, website, order, options):
        result = super(ProductTemplate, self)._search_get_detail(website, order, options)
        if options.get('displayDescription'):
            result['search_fields'].append('description_website')
            result['fetch_fields'].append('description_website')
        return result