import { patch } from "@web/core/utils/patch";
import { markup } from "@odoo/owl";
import { setElementContent } from "@web/core/utils/html";
import { ProductPage } from "@website_sale/interactions/product_page";

patch(ProductPage.prototype, {
    /**
     * Render the installment plans of the selected variant.
     */
    async _onChangeCombination(ev, parent, combination) {
        await super._onChangeCombination(...arguments);
        const container = parent.querySelector(".o_wsale_installment_plans");
        if (container && "installment_plans" in combination) {
            setElementContent(container, markup(combination.installment_plans));
        }
    },
});
