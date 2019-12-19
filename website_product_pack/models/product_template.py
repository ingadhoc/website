##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.constrains('website_published')
    def set_website_published_for_packs_lines_products(self):
        for rec in self.filtered(lambda x: x.pack_ok and x.website_published):
            rec.pack_line_ids.mapped('product_id').filtered(
                lambda p: not p.website_published or not p.sale_ok).write({
                    'website_published': True,
                    'sale_ok': True,
                })
        # for product who used in product pack set the parent unpublished
        for rec in self.filtered(
                lambda x: not x.website_published and x.used_in_pack_line_ids):
            rec.used_pack_line_ids.mapped('parent_product_id').filtered(
                'website_published').write(
                {'website_published': False})
