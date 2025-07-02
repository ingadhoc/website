from odoo.addons.website_sale.controllers import main
from odoo.tools.translate import _


class WebsiteSale(main.WebsiteSale):
    def _get_shop_payment_values(self, order, **kwargs):
        payment_values = super()._get_shop_payment_values(order=order, **kwargs)
        payment_values["submit_button_label"] = _("Complete Purchase")
        return payment_values
