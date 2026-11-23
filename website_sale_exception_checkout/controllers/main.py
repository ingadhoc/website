from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteSaleExceptionCheckout(WebsiteSale):
    def _get_website_exception_title(self, order):
        return order.env._("We can't process your order")

    def _get_shop_payment_errors(self, order):
        errors = super()._get_shop_payment_errors(order)
        title = self._get_website_exception_title(order)
        for message in order._get_website_exceptions()._get_website_messages():
            errors.append((title, message))
        return errors

    def _get_shop_payment_values(self, order, **kwargs):
        values = super()._get_shop_payment_values(order, **kwargs)
        title = self._get_website_exception_title(order)
        values["show_back_to_cart"] = any(error[0] == title for error in values["errors"])
        return values
