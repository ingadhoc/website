##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, api, _
from odoo.exceptions import ValidationError


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.constrains('pack_line_ids')
    def check_website_published(self):
        for rec in self.filtered('website_published'):
            unpublished = rec.pack_line_ids.mapped('product_id').filtered(
                lambda x: not x.website_published)
            if unpublished:
                raise ValidationError(_(
                    "You can't add unpublished products (%s) to a published "
                    "pack (%s)") % (
                        ', '.join(unpublished.mapped('name')),
                        rec.name))
