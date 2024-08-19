/** @odoo-module **/

import {registry} from "@web/core/registry";

registry.category("web_tour.tours").add("website_sale_search_improved_tour", {
    url: "/shop",
    test: true,
    steps: () =>  [
        {
            trigger: 'form input[name="search"]',
            run: "text Test Description",
        },
        {
            content: "Select the product from the search results (description)",
            trigger: '.o_dropdown_menu:first .dropdown-item:contains("Test Product")',
            run: "click"
        },
        {
            content: "Verify the selected product is correct.",
            trigger: 'div[data-oe-expression="product.description_ecommerce"]:contains("Test Description")',
            run: function () {}, // it's a check
        },
        {
            trigger: 'form input[name="search"]',
            run: "text Test Tag",
        },
        {
            content: "Select the product from the search results (tag)",
            trigger: '.o_dropdown_menu:first .dropdown-item:contains("Test Product")',
            run: "click"
        },
        {
            content: "Verify the selected product is correct.",
            trigger: 'span[data-oe-expression="tag.name"]:contains("Test Tag")',
            run: function () {}, // it's a check
        },
    ]
});

