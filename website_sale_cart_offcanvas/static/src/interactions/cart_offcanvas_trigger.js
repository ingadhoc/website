import { registry } from "@web/core/registry";
import { Interaction } from "@web/public/interaction";
import { getCartOffcanvasEl, isCartPage } from "@website_sale_cart_offcanvas/js/cart_offcanvas_utils";

/**
 * Open the cart panel from the header cart icon.
 *
 * The selector matches both the desktop and the mobile header, which each render
 * `website_sale.header_cart_link` once.
 */
export class CartOffcanvasTrigger extends Interaction {
    static selector = "li.o_wsale_my_cart";

    dynamicContent = {
        "a[href$='/shop/cart']": { "t-on-click": this.onCartIconClick },
    };

    onCartIconClick(ev) {
        const panelEl = getCartOffcanvasEl();
        if (!panelEl || isCartPage()) {
            return; // no panel: the link keeps navigating
        }
        ev.preventDefault();
        window.Offcanvas.getOrCreateInstance(panelEl).show();
    }
}

registry
    .category("public.interactions")
    .add("website_sale_cart_offcanvas.cart_offcanvas_trigger", CartOffcanvasTrigger);
