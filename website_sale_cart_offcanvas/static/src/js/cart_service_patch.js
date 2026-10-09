import { patch } from "@web/core/utils/patch";
import { CartService } from "@website_sale/js/cart_service";
import { getCartOffcanvasEl, isCartPage } from "@website_sale_cart_offcanvas/js/cart_offcanvas_utils";

patch(CartService.prototype, {
    /**
     * Open the cart panel instead of the "item added" notification.
     *
     * Patching the service covers every "add to cart" origin at once, and runs after the
     * configurator dialog when the product has variants, options or is a combo.
     */
    _showCartNotification(notification) {
        const panelEl = getCartOffcanvasEl();
        // Warnings are errors, not cart content: they keep using the standard notification.
        if (!panelEl || isCartPage() || notification.type !== "item_added") {
            return super._showCartNotification(notification);
        }
        window.Offcanvas.getOrCreateInstance(panelEl).show();
    },
});
