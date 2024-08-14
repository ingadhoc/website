/** @odoo-module **/

import tour from 'web_tour.tour';
import tourUtils from 'website_sale.tour_utils';

tour.register('website_sale_tour_wire_transfer', {
    test: true,
    url: '/shop',
},
    [
        {
            content: "Search for the product 'Test Product'.",
            trigger: 'form input[name="search"]',
            run: "text Test Product",
        },
        {
            content: "Click the search button.",
            trigger: 'form:has(input[name="search"]) .oe_search_button',
        },
        {
            content: "Select the product 'Test Product' from the search results.",
            trigger: '.oe_product_cart:first a:contains("Test Product")',
            run: "click"
        },
        {
            content: "Add one more quantity of the product.",
            trigger: '.css_quantity a.js_add_cart_json i.fa-plus',
        },
        {
            content: "Click on add to cart.",
            trigger: "a[id='add_to_cart']",
            run: "click"
        },
        tourUtils.goToCart({quantity: 2}),
        {
            content: "Verify the selected product is in the cart.",
            trigger: '#cart_products tbody td.td-product_name a strong:contains("Test Product")',
            run: function () {}, // it's a check
        },
        {
            content: "Verify there are 2 quantities of the product in the cart.",
            trigger: '#cart_products tbody td.td-qty div.css_quantity input[value=2]',
            run: function () {}, // it's a check
        },
        {
            content: "Proceed to checkout.",
            extra_trigger: '#cart_products .oe_currency_value:contains(121.00)',
            trigger: 'a[href*="/shop/checkout?express=1"]',
            run: "click"
        },
        {
            content: "Select Wire Transfer as the payment method.",
            trigger: 'div:contains("Wire Transfer") input',
            run: "click"
        },
        {
            content: "Click the payment submit button.",
            trigger: 'button[name="o_payment_submit_button"]',
            run: "click"
        },
        {
            content: "finish",
            trigger: "strong:contains('Payment Information:')",
            run: function () {
                window.location.href = '/contactus';
            },
            timeout: 30000,
        },
        {
            content: "wait page loaded",
            trigger: 'h1:contains("Contact us")',
            run: function () {}, // it's a check
        },
    ]
);

tour.register('website_sale_tour_demo', {
    test: true,
    url: '/shop',
},
    [
        {
            content: "Search for the product 'Test Product'.",
            trigger: 'form input[name="search"]',
            run: "text Test Product",
        },
        {
            content: "Click the search button.",
            trigger: 'form:has(input[name="search"]) .oe_search_button',
        },
        {
            content: "Select the product 'Test Product' from the search results.",
            trigger: '.oe_product_cart:first a:contains("Test Product")',
            run: "click"
        },
        {
            content: "Add one more quantity of the product.",
            trigger: '.css_quantity a.js_add_cart_json i.fa-plus',
        },
        {
            content: "Click on add to cart.",
            trigger: "a[id='add_to_cart']",
            run: "click"
        },
        tourUtils.goToCart({quantity: 2}),
        {
            content: "Verify the selected product is in the cart.",
            trigger: '#cart_products tbody td.td-product_name a strong:contains("Test Product")',
            run: function () {}, // it's a check
        },
        {
            content: "Verify there are 2 quantities of the product in the cart.",
            trigger: '#cart_products tbody td.td-qty div.css_quantity input[value=2]',
            run: function () {}, // it's a check
        },
        {
            content: "Proceed to checkout.",
            extra_trigger: '#cart_products .oe_currency_value:contains(121.00)',
            trigger: 'a[href*="/shop/checkout?express=1"]',
            run: "click"
        },
        {
            content: "Select the demo payment method.",
            trigger: 'b:contains("Demo")',
            run: function () {
                this.$anchor[0].parentElement.parentElement.querySelector('input').id = 'demo'
            },
        },
        {
            content: "Click the demo payment method.",
            trigger: '#demo',
            run: "click"
        },
        {
            content: "Enter customer input.",
            trigger: 'input[name="customer_input"]',
            run: "text 1111"
        },
        {
            content: "Click the payment submit button.",
            trigger: 'button[name="o_payment_submit_button"]',
            run: "click"
        },
        {
            content: "finish",
            trigger: "strong:contains('Payment Information:')",
            run: function () {
                window.location.href = '/contactus';
            },
            timeout: 30000,
        },
        {
            content: "wait page loaded",
            trigger: 'h1:contains("Contact us")',
            run: function () {}, // it's a check
        },
    ]
);
