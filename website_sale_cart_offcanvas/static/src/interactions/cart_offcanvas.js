import { markup } from "@odoo/owl";
import { rpc } from "@web/core/network/rpc";
import { registry } from "@web/core/registry";
import { setElementContent } from "@web/core/utils/html";
import { Interaction } from "@web/public/interaction";
import { updateCartIcon } from "@website_sale_cart_offcanvas/js/cart_offcanvas_utils";

export class CartOffcanvas extends Interaction {
    static selector = "#o_wsale_cart_offcanvas";

    dynamicContent = {
        _root: { "t-on-show.bs.offcanvas": this.onShow },
    };

    async onShow() {
        const bodyEl = this.el.querySelector(".offcanvas-body");
        const data = await this.waitFor(rpc("/shop/cart/offcanvas", {}));
        // Interactions must be stopped before and started after injecting the fragment:
        // without it the injected nodes stay inert and nothing is logged.
        this.services["public.interactions"].stopInteractions(bodyEl);
        setElementContent(bodyEl, markup(data.content));
        this.services["public.interactions"].startInteractions(bodyEl);
        updateCartIcon(data.cart_quantity);
    }
}

registry
    .category("public.interactions")
    .add("website_sale_cart_offcanvas.cart_offcanvas", CartOffcanvas);
