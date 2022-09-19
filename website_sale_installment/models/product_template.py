from odoo import fields, models


class ProductTemplate(models.Model):

    _inherit = 'product.template'

    def _website_installment_tree(self):
        self.ensure_one()
        current_website = self.env['website'].get_current_website()
        installment_ids = self.env['account.card.installment'].sudo().search([
            ('card_id.website_published', '=', True)
        ])
        pricelist = current_website.get_current_pricelist()

        context = dict(self.env.context, quantity=1, pricelist=pricelist.id)
        product_template = self.with_context(context)
        list_price = product_template.price_compute('list_price')[product_template.id]
        tax_price = product_template.taxes_id.compute_all(list_price)['total_included']
        return installment_ids.card_installment_tree(tax_price)

    def _website_installment_variant_tree(self, product_id):
        self.ensure_one()
        current_website = self.env['website'].get_current_website()
        installment_ids = self.env['account.card.installment'].sudo().search([
            ('card_id.website_published', '=', True)
        ])
        pricelist = current_website.get_current_pricelist()
        combination_info = self._get_combination_info(product_id=product_id, add_qty=1, pricelist=pricelist)
        return installment_ids.card_installment_tree(combination_info['list_price'])

    def _get_combination_info(self, combination=False, product_id=False, add_qty=1, pricelist=False, parent_combination=False, only_template=False):

        combination_info = super()._get_combination_info(combination, product_id,
                                                         add_qty, pricelist, parent_combination, only_template)
        combination_info['installment_price'] = []
        if self.env.context.get('website_id'):
            website = self.env['website'].get_current_website()
            if website.installment_price_ids:
                combination_info['installment_price'] = website.installment_price_ids.card_installment_tree(combination_info['price'])

        return combination_info

