##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields
import logging
_logger = logging.getLogger(__name__)


class ProductAttribute(models.Model):
    _inherit = 'product.attribute'

    website_link_on_product = fields.Boolean(
        default=True,
        help='Add a link on website product view so that user can click on an '
        'attribute value and go to a search of products of that value'
    )


class ProductTemplateAttributeLine(models.Model):
    _inherit = 'product.template.attribute.line'

    def _prepare_single_value(self):
        """On the product page group together the attribute lines that concern
        the same attribute and that have only one value each.

        Indeed those are considered informative values, they do not generate
        choice for the user, so they are displayed below the configurator.

        The returned attributes are ordered as they appear in `self`, so based
        on the order of the attribute lines.
        """
        single_value_lines = self.filtered(lambda ptal: len(ptal.value_ids) == 1)
        return single_value_lines
