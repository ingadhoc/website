# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, fields, api


class website_promotion(models.Model):
    _name = 'website.promotion'
    _description = 'Website Promotion'

    name = fields.Char(
        'Name',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]}
    )
    pricelist_id = fields.Many2one(
        'product.pricelist',
        'Pricelist',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]}
    )
    public_category_id = fields.Many2one(
        'product.public.category',
        'Public Category',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]}

    )
    template_ids = fields.Many2many(
        'product.template',
        'website_promotion_product_rel',
        'website_promotion_id',
        'product_id',
        'Product Template',
        readonly=True,
        states={'draft': [('readonly', False)]}
    )
    website_style_id = fields.Many2one(
        'product.style',
        'Website Style',
        readonly=True,
        states={'draft': [('readonly', False)]}
    )
    state = fields.Selection(
        [('draft', 'Draft'),
         ('confirm', 'Confirm'),
         ('finished', 'Finished')
         ],
        default='draft',
        string='State'
    )
    base = fields.Selection([
        ('list_price', 'Public Price'),
        ('standard_price', 'Cost'),
        ('pricelist', 'Other Pricelist')],
        'Based on',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]}
    )
    price_discount = fields.Float(
        'Price Discount',
        readonly=True,
        states={'draft': [('readonly', False)]})
    price_surcharge = fields.Float(
        'Price Surcharge',
        readonly=True,
        states={'draft': [('readonly', False)]})
    base_pricelist_id = fields.Many2one(
        'product.pricelist',
        'Other Pricelist',
        readonly=True,
        states={'draft': [('readonly', False)]})

    @api.one
    def to_draft(self):
        self.state = 'draft'

    @api.one
    def confirm(self):
        self.state = 'confirm'
        if self.website_style_id:
            self.template_ids.write(
                {'website_style_ids': [(4, self.website_style_id.id)]})
        self.template_ids.write(
            {'public_categ_ids': [(4, self.public_category_id.id)]})
        for product in self.template_ids:
            vals = {
                'name': self.name,
                'applied_on': '1_product',
                'product_tmpl_id': product.id,
                'sequence': 0,
                'base': self.base,
                'base_pricelist_id': self.base_pricelist_id.id,
                'pricelist_id': self.pricelist_id.id,
                'price_discount': self.price_discount,
                'compute_price': 'formula',
                'price_surcharge': self.price_surcharge,
            }
            self.env['product.pricelist.item'].create(vals)

    @api.one
    def finished(self):
        self.state = 'finished'
        prod_pricelist_item_obj = self.env['product.pricelist.item']
        domain = [
            ('name', '=', self.name),
            ('sequence', '=', 0),
            ('pricelist_id', '=', self.pricelist_id.id),
            ('product_tmpl_id', 'in', self.template_ids.ids)
        ]
        items = prod_pricelist_item_obj.search(domain)
        if items:
            items.unlink()
        if self.website_style_id:
            self.template_ids.write(
                {'website_style_ids': [(3, self.website_style_id.id)]})
        self.template_ids.write(
            {'public_categ_ids': [(3, self.public_category_id.id)]})
