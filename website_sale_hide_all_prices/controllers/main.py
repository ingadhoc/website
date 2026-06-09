import json

from odoo import http
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.http import request
from odoo.tools.translate import _


class WebsiteSale(WebsiteSale):
    @http.route(["/shop/confirmation"], type="http", auth="public", website=True, sitemap=False)
    def shop_payment_confirmation(self, **post):
        sale_order_id = request.session.get("sale_last_order_id")

        if sale_order_id:
            order = request.env["sale.order"].sudo().browse(sale_order_id)
            if order and order.website_id.website_hide_all_prices:
                return request.redirect("/request-quotation")

        return super().shop_payment_confirmation(**post)

    def _get_shop_payment_values(self, order, **kwargs):
        payment_values = super()._get_shop_payment_values(order=order, **kwargs)
        if order and order.website_id.website_hide_all_prices:
            payment_values["submit_button_label"] = _("Request Quotation")
        return payment_values

    def _confirm_quotation_request(self, order_sudo):
        """Finalize a quotation request (no payment).

        The cart is left as a draft quotation for the sales team to follow up
        on; its last id is stashed for the thank-you page and the cart session
        is reset so the customer gets a fresh cart.
        """
        order_sudo._recompute_cart()
        request.session["sale_last_order_id"] = order_sudo.id
        request.website.sale_reset()

    @http.route(
        ["/shop/request_quotation"],
        type="http",
        auth="public",
        methods=["POST"],
        website=True,
        sitemap=False,
    )
    def shop_request_quotation(self, **post):
        """Skip the payment step when the website hides all prices.

        Instead of routing the customer through /shop/payment (there is no real
        payment for a quotation request), confirm the quotation request and land
        the customer on the 'request received' thank-you page. Used as a fallback
        for customers that reach /shop/checkout directly (e.g. logged-in users
        with a saved address).
        """
        order_sudo = request.cart

        if redirection := self._check_cart_and_addresses(order_sudo):
            return redirection

        # If the module is not active for this website, keep the native flow.
        if not (order_sudo.website_id and order_sudo.website_id.website_hide_all_prices):
            return request.redirect("/shop/payment")

        self._confirm_quotation_request(order_sudo)
        return request.redirect("/request-quotation")

    @http.route(
        ["/shop/address/submit"],
        type="http",
        methods=["POST"],
        auth="public",
        website=True,
        sitemap=False,
    )
    def shop_address_submit(
        self,
        partner_id=None,
        address_type="billing",
        use_delivery_as_billing=None,
        callback=None,
        **form_data,
    ):
        """Bypass the intermediate /shop/checkout step for quotation websites.

        Once the address form is saved and the cart's addresses are complete,
        confirm the quotation request and redirect straight to the thank-you
        page instead of the checkout review step. Falls back to the native flow
        when the module is inactive, an explicit callback was requested, the
        save failed, or the addresses are still incomplete.
        """
        result = super().shop_address_submit(
            partner_id=partner_id,
            address_type=address_type,
            use_delivery_as_billing=use_delivery_as_billing,
            callback=callback,
            **form_data,
        )

        order_sudo = request.cart
        # Respect an explicit callback (e.g. editing an address from elsewhere)
        # and only act for websites that hide all prices.
        if callback or not (order_sudo and order_sudo.website_id.website_hide_all_prices):
            return result

        # The @route-decorated parent returns a wrapped Response, not the raw
        # JSON string; read its body to inspect/rewrite the feedback.
        if isinstance(result, str):
            body = result
        elif hasattr(result, "get_data"):
            body = result.get_data(as_text=True)
        else:
            return result
        try:
            feedback = json.loads(body)
        except (TypeError, ValueError):
            return result  # Not a JSON feedback (e.g. a redirect): keep native flow.

        if feedback.get("invalid_fields") or not feedback.get("redirectUrl"):
            return result  # Save failed: keep the native error handling.

        if self._check_cart_and_addresses(order_sudo):
            return result  # Addresses still incomplete: keep the native flow.

        self._confirm_quotation_request(order_sudo)
        feedback["redirectUrl"] = "/request-quotation"
        return json.dumps(feedback)
