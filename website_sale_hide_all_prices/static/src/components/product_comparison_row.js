import { ProductRow } from "@website_sale_comparison/js/product_row/product_row";
import { patch } from "@web/core/utils/patch";
import { session } from "@web/session";

patch(ProductRow.prototype, {
    get websiteHideAllPrices() {
        return !!session.website_hide_all_prices;
    },
});
