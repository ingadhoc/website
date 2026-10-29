import { patch } from "@web/core/utils/patch";
import { ProductPage } from "@website_sale/interactions/product_page";

patch(ProductPage.prototype, {
    /**
     * Override of `website_sale` to show the internal reference of the selected variant.
     *
     * @param {Event} ev
     * @param {Element} parent
     * @param {Object} combination
     */
    async _onChangeCombination(ev, parent, combination) {
        await super._onChangeCombination(...arguments);
        // `parent` is the `.js_product` form; the reference sits next to it, under the details.
        const details = parent.closest("#product_details") ?? document;
        const internalRef = details.querySelector(".o_wsale_ux_internal_ref");
        if (!internalRef) {
            return;
        }
        const defaultCode = combination.default_code;
        internalRef.querySelector(".o_wsale_ux_internal_ref_value").textContent = defaultCode || "";
        internalRef.classList.toggle("d-none", !defaultCode);
    },
});
