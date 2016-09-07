# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, fields
# from openerp.exceptions import Warning
import logging
_logger = logging.getLogger(__name__)


class ProductAttribute(models.Model):
    _inherit = 'product.attribute'

    website_link_on_product = fields.Boolean(
        default=True,
        help='Add a link on website product view so that user can click on an '
        'attribute value and go to a search of products of that value'
    )
