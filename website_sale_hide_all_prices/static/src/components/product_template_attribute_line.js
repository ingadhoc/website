import { ProductTemplateAttributeLine } from "@sale/js/product_template_attribute_line/product_template_attribute_line";
import { patch } from "@web/core/utils/patch";

patch(ProductTemplateAttributeLine.prototype, {
    /**
     * Drop the "(+ $X)" extra-price suffix of the dropdown options when prices
     * are hidden. `env.showPrice` is set by the product configurator dialog
     * (false when the website hides all prices); it is only undefined outside
     * that subtree, where the native behaviour must be preserved.
     */
    getPTAVSelectName(ptav) {
        if (this.env.showPrice === false) {
            return ptav.name;
        }
        return super.getPTAVSelectName(ptav);
    },
});
