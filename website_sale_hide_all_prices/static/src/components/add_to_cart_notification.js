import { session } from "@web/session";
import { ItemAddedNotification } from "@website_sale/js/cart_notification/item_added_notification/item_added_notification";
import { patch } from "@web/core/utils/patch";

patch(ItemAddedNotification.prototype, {
    get websiteHideAllPrices() {
        return !!session.website_hide_all_prices;
    },
});
