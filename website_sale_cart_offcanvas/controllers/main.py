##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo.http import Controller, request, route


class CartOffcanvas(Controller):
    @route(
        route="/shop/cart/offcanvas",
        type="jsonrpc",
        auth="public",
        methods=["POST"],
        website=True,
        sitemap=False,
    )
    def cart_offcanvas(self, **kwargs):
        """Render the cart panel content.

        The fragment is only ever served over RPC, never inlined in the page, so a page
        cache can never serve one visitor's cart to another.
        """
        order_sudo = request.cart
        return {
            "cart_quantity": order_sudo.cart_quantity if order_sudo else 0,
            "content": request.env["ir.ui.view"]._render_template(
                "website_sale_cart_offcanvas.cart_offcanvas_content",
                {"website_sale_order": order_sudo},
            ),
        }
