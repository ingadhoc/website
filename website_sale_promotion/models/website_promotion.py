# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, fields, api, _


class website_promotion(models.Model):
    _name = 'website.promotion'
    _description = 'Website Promotion'

    @api.model
    def _price_field_get(self):
        result = []
        # for line in self.env['product.price.type'].search([]):
        #     result.append((str(line.id), line.name))
        result.append(('-1', _('Other Pricelist')))
        result.append(('-2', _('Supplier Prices on the product form')))
        return result

    name = fields.Char(
        'Name',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]}
    )
    # pricelist_version_id = fields.Many2one(
    #     'product.pricelist.version',
    #     'Pricelist Version',
    #     required=True,
    #     readonly=True,
    #     states={'draft': [('readonly', False)]}
    # )
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
    price_discount = fields.Float(
        'Price Discount',
        readonly=True,
        states={'draft': [('readonly', False)]})
    price_surcharge = fields.Float(
        'Price Surcharge',
        readonly=True,
        states={'draft': [('readonly', False)]})
    base = fields.Selection(
        _price_field_get,
        'Based on',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]}
    )
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
                'product_tmpl_id': product.id,
                'sequence': 0,
                'base': int(self.base),
                'base_pricelist_id': self.base_pricelist_id.id,
                # 'price_version_id': self.pricelist_version_id.id,
                'price_discount': self.price_discount,
                'price_surcharge': self.price_surcharge,
            }
            self.env['product.pricelist.item'].create(vals)

    @api.one
    def finished(self):
        self.state = 'finished'
        prod_pricelist_item_obj = self.env['product.pricelist.item']
        domain = [
            ('name', '=', self.name),
            # ('price_version_id', '=', self.pricelist_version_id.id),
            ('sequence', '=', 0),
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
