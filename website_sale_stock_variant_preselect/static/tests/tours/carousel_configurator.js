import { registry } from "@web/core/registry";
import * as tourUtils from "@website_sale/js/tours/tour_utils";

registry.category("web_tour.tours").add("website_sale_stock_variant_preselect_carousel", {
    url: "/preselect-carousel",
    steps: () => [
        {
            content: "Click 'Add to cart' on the carousel card of the template",
            trigger: ".o_carousel_product_card:contains('Preselect test product')",
            run() {
                // The button only shows on hover, depending on the shop design options.
                document.querySelector(".o_carousel_product_card .js_add_cart").click();
            },
        },
        {
            content: "The configurator opens on Green, the first variant with stock",
            trigger: ".o_sale_product_configurator_dialog .form-check:has(input:checked) label:contains('Green')",
        },
        {
            content: "Confirm the configurator",
            trigger: 'button[name="website_sale_product_configurator_continue_button"]',
            run: "click",
        },
        tourUtils.goToCart(),
        ...tourUtils.assertCartContains({
            productName: "Preselect test product",
            combinationName: "Green",
        }),
    ],
});
