import { ProductPage } from "@website_sale/interactions/product_page";
import { patch } from "@web/core/utils/patch";
import { session } from "@web/session";

patch(ProductPage.prototype, {
    onHoverPackagingButton(ev) {
        if (session.website_hide_all_prices) {
            return;
        }
        return super.onHoverPackagingButton(...arguments);
    },
});
