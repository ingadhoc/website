import { patch } from "@web/core/utils/patch";
import { CartService } from "@website_sale/js/cart_service";
import { getCartOffcanvasEl, isCartPage } from "@website_sale_cart_offcanvas/js/cart_offcanvas_utils";

patch(CartService.prototype, {
    /**
     * Open the cart panel instead of the "lines added" toast.
     *
     * Patching the service covers every "add to cart" origin at once, and runs after the
     * configurator dialog when the product has variants, options or is a combo.
     */
    _showCartNotification(props, options = {}) {
        const panelEl = getCartOffcanvasEl();
        if (!panelEl || isCartPage() || !props.lines) {
            return super._showCartNotification(props, options);
        }
        // Warnings are errors, not cart content: they keep using the standard notification.
        if (props.warning) {
            super._showCartNotification({ warning: props.warning }, options);
        }
        window.Offcanvas.getOrCreateInstance(panelEl).show();
    },
});
