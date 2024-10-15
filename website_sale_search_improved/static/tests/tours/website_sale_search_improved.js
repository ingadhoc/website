/** @odoo-module **/

import {registry} from "@web/core/registry";
import tourUtils from '@website_sale/js/tours/tour_utils';


registry.category("web_tour.tours").add("website_sale_search_improved_tour", {
    url: "/shop",
    test: true,
    steps: () =>  [
         ...tourUtils.searchProduct("Test Description"),
         {
            content: "Verify the selected product is correct.",
            trigger: 'a[data-oe-expression="product.name"]:contains("Test Product")',
            run: function () {}, // it's a check
        },
         ...tourUtils.searchProduct("Test Tag"),
         {
            content: "Verify the selected product is correct.",
            trigger: 'a[data-oe-expression="product.name"]:contains("Test Product")',
            run: function () {}, // it's a check
        }
    ]
});

