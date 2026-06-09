import { useSubEnv } from "@odoo/owl";
import { ProductConfiguratorDialog } from "@sale/js/product_configurator_dialog/product_configurator_dialog";
import { patch } from "@web/core/utils/patch";
import { session } from "@web/session";

patch(ProductConfiguratorDialog.prototype, {
    setup() {
        super.setup(...arguments);
        useSubEnv({
            showPrice: !session.website_hide_all_prices,
        });
    },
});
