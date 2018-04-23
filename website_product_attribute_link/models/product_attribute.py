# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from openerp import models, fields
import logging
_logger = logging.getLogger(__name__)


class ProductAttribute(models.Model):
    _inherit = 'product.attribute'

    website_link_on_product = fields.Boolean(
        default=True,
        help='Add a link on website product view so that user can click on an '
        'attribute value and go to a search of products of that value'
    )
