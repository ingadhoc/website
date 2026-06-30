/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";
import "@website_sale/js/website_sale";

/*
 * RG 4/2025 forces us to show both prices (with and without national taxes) in
 * the e-commerce. The tax-excluded price is rendered server-side, but it must
 * also be refreshed when the customer picks another variant on the product
 * page, mirroring how Odoo updates the regular price on combination change.
 *
 * We include the WebsiteSale widget (not the VariantMixin) because the widget
 * copies the mixin methods into its prototype at definition time, so patching
 * the mixin afterwards from this asset would never reach the widget instance.
 */
publicWidget.registry.WebsiteSale.include({
    _onChangeCombination(ev, $parent, combination) {
        this._super.apply(this, arguments);
        if (combination.price_tax_excluded !== undefined) {
            $parent.find(".o_l10n_ar_price_tax_excluded .oe_currency_value").text(
                this._priceToStr(combination.price_tax_excluded, combination.currency_precision)
            );
        }
    },
});
