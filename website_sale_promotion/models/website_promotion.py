##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields, api


class WebsitePromotion(models.Model):
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

    @api.multi
    def to_draft(self):
        for rec in self:
            rec.state = 'draft'

    @api.multi
    def confirm(self):
        for rec in self:
            rec.state = 'confirm'
            if rec.website_style_id:
                rec.template_ids.write(
                    {'website_style_ids': [(4, rec.website_style_id.id)]})
            rec.template_ids.write(
                {'public_categ_ids': [(4, rec.public_category_id.id)]})
            vals_list = [
                {
                    'name': rec.name,
                    'applied_on': '1_product',
                    'product_tmpl_id': product.id,
                    'base': rec.base,
                    'base_pricelist_id': rec.base_pricelist_id.id,
                    'pricelist_id': rec.pricelist_id.id,
                    'price_discount': rec.price_discount,
                    'compute_price': 'formula',
                    'price_surcharge': rec.price_surcharge,
                } for product in rec.template_ids]
            self.env['product.pricelist.item'].create(vals_list)

    @api.multi
    def finished(self):
        for rec in self:
            rec.state = 'finished'
            prod_pricelist_item_obj = self.env['product.pricelist.item']
            domain = [
                ('name', '=', rec.name),
                ('pricelist_id', '=', rec.pricelist_id.id),
                ('product_tmpl_id', 'in', rec.template_ids.ids)
            ]
            items = prod_pricelist_item_obj.search(domain)
            if items:
                items.unlink()
            if rec.website_style_id:
                rec.template_ids.write(
                    {'website_style_ids': [(3, rec.website_style_id.id)]})
            rec.template_ids.write(
                {'public_categ_ids': [(3, rec.public_category_id.id)]})
