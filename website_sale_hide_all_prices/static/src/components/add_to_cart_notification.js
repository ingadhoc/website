import { session } from "@web/session";
import { AddToCartNotification } from "@website_sale/js/notification/add_to_cart_notification/add_to_cart_notification";
import { patch } from "@web/core/utils/patch";

patch(AddToCartNotification.prototype, {
    get websiteHideAllPrices() {
        return !!session.website_hide_all_prices;
    },
});

AddToCartNotification.template = "website_sale_hide_all_prices.MyAddToCartNotification";
