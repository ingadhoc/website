from odoo import models

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def _get_published_installments(self):
        return self.env['account.card.installment'].sudo().search([
            ('is_published', '=', True)
        ])

    def _get_installment_plans(self, price):
        plans = []
        for cuota in self._get_published_installments():
            values = cuota.map_installment_values(price)
            plans.append({
                'installments': cuota.installment,
                'description': values['description'],
                'messagge': cuota.messagge or '',
            })
        return plans

    def _get_combination_info(self, combination=False, product_id=False, add_qty=1, pricelist=False, parent_combination=False, only_template=False):
        combination_info = super()._get_combination_info(
            combination=combination,
            product_id=product_id,
            add_qty=add_qty,
            pricelist=pricelist,
            parent_combination=parent_combination,
            only_template=only_template
        )

        product_price = combination_info.get('price', 0)
        installment_plans = self._get_installment_plans(product_price)
        combination_info.update({'installment_plans': installment_plans})

        return combination_info

    def _get_card_installments_for_shop(self, context_price):
        installment_plans = self._get_installment_plans(context_price)

        return installment_plans
