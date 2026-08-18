from odoo import models
from odoo.http import request


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def _get_additionnal_combination_info(self, product_or_template, quantity, uom, date, website):
        """Corregimos el precio sin impuestos nacionales de la ficha de producto.

        `l10n_ar_website_sale` lo calcula sobre el precio de la lista de precios
        (que ya viene con el descuento aplicado) y despues le vuelve a restar
        ese mismo descuento, con lo cual el valor queda por debajo del real. Lo
        recalculamos sin ese ajuste, igual que en la pagina de la tienda.
        """
        combination_info = super()._get_additionnal_combination_info(product_or_template, quantity, uom, date, website)

        if "l10n_ar_price_tax_excluded" not in combination_info:
            return combination_info

        currency = combination_info["currency"]
        pricelist_price, _rule_id = request.pricelist._get_product_price_rule(
            product=product_or_template,
            quantity=quantity,
            uom=uom,
            currency=currency,
        )
        # Misma adaptacion de base imponible que hace `website_sale` antes de aplicar
        # los impuestos, para el caso de un impuesto incluido remapeado por posicion fiscal.
        pricelist_price = self.env["product.product"]._get_tax_included_unit_price_from_price(
            pricelist_price,
            combination_info["product_taxes"],
            product_taxes_after_fp=combination_info["taxes"],
        )
        combination_info["l10n_ar_price_tax_excluded"] = combination_info["taxes"].compute_all(
            pricelist_price, currency, 1, product_or_template, self.env.user.partner_id
        )["total_excluded"]

        return combination_info
