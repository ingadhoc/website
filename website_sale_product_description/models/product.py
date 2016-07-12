# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
import logging
from openerp import fields, models
_logger = logging.getLogger(__name__)


# configAuthorization.set('PRISMA f3d8b72c94ab4a06be2ef7c95490f7d3')

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    description_website = fields.Text(
        'Sale Description',
        translate=True,
        help="A description of the Product that you want to communicate on the"
        " ecommerce to your customers. This description will not be used on "
        "Sales Orders, Deliveries and Invoices"
    )
