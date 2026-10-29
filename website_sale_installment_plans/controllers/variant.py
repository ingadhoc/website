from odoo.addons.website_sale.controllers.variant import WebsiteSaleVariantController
from odoo.http import route


class WebsiteSaleInstallmentVariantController(WebsiteSaleVariantController):
    @route()
    def get_combination_info_website(
        self, product_template_id, product_id, combination, add_qty, uom_id=None, **kwargs
    ):
        combination_info = super().get_combination_info_website(
            product_template_id, product_id, combination, add_qty, uom_id=uom_id, **kwargs
        )
        product_template = self.env["product.template"].browse(int(product_template_id))
        combination_info["installment_plans"] = self.env.website._render_template(
            "website_sale_installment_plans.installment_plans",
            values={
                "installment_plans": product_template._get_installment_plans(
                    0 if combination_info["hide_price"] else combination_info["price"]
                ),
            },
        )
        return combination_info
