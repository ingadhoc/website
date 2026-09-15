/** @odoo-module **/

import { registry } from "@web/core/registry";
import * as tourUtils from "@website_sale/js/tours/tour_utils";

const PANEL = "#o_wsale_cart_offcanvas.show";

registry.category("web_tour.tours").add("website_sale_cart_offcanvas_add_from_product", {
    url: "/shop",
    steps: () => [
        ...tourUtils.addToCart({ productName: "Offcanvas Product" }),
        {
            content: "The panel is open",
            trigger: `${PANEL} .o_wsale_cart_offcanvas_content`,
        },
        {
            content: "The panel lists the product",
            trigger: `${PANEL} .o_cart_product:contains("Offcanvas Product")`,
        },
        {
            content: "The panel shows the total",
            trigger: `${PANEL} .o_cart_total:contains("100.00")`,
        },
        {
            content: "Checkout goes to the cart page",
            trigger: `${PANEL} a[href="/shop/cart"]`,
            run: "click",
            expectUnloadPage: true,
        },
        {
            content: "The cart page shows the same total",
            trigger: '#shop_cart .o_cart_total:contains("100.00")',
        },
    ],
});

registry.category("web_tour.tours").add("website_sale_cart_offcanvas_header_empty", {
    url: "/shop",
    steps: () => [
        {
            content: "Click the header cart icon",
            trigger: "li.o_wsale_my_cart a",
            run: "click",
        },
        {
            content: "The panel opens on the empty state",
            trigger: `${PANEL} .o_wsale_cart_offcanvas_empty`,
        },
        {
            content: "We did not leave the shop",
            trigger: ".oe_website_sale",
        },
    ],
});

registry.category("web_tour.tours").add("website_sale_cart_offcanvas_close_on_backdrop", {
    url: "/shop",
    steps: () => [
        {
            content: "Click the header cart icon",
            trigger: "li.o_wsale_my_cart a",
            run: "click",
        },
        {
            content: "The panel is open",
            trigger: `${PANEL} .offcanvas-body`,
        },
        {
            content: "Click outside the panel",
            trigger: ".offcanvas-backdrop",
            run: "click",
        },
        {
            content: "The panel is closed and the page is untouched",
            trigger: "#o_wsale_cart_offcanvas:not(.show)",
        },
        {
            content: "We are still on the shop",
            trigger: ".oe_website_sale",
        },
    ],
});

registry.category("web_tour.tours").add("website_sale_cart_offcanvas_configurator", {
    url: "/shop",
    steps: () => [
        ...tourUtils.searchProduct("Offcanvas Configurable"),
        {
            content: "Open the product page",
            trigger: 'a:contains("Offcanvas Configurable")',
            run: "click",
            expectUnloadPage: true,
        },
        {
            content: "Add to cart",
            trigger: "#add_to_cart",
            run: "click",
        },
        {
            content: "The configurator is open and the panel is not",
            trigger: ".o_sale_product_configurator_dialog:not(:has(#o_wsale_cart_offcanvas.show))",
        },
        {
            content: "Confirm the configurator",
            trigger: 'button[name="website_sale_product_configurator_continue_button"]',
            run: "click",
        },
        {
            content: "Only now the panel opens",
            trigger: `${PANEL} .o_cart_product:contains("Offcanvas Configurable")`,
        },
    ],
});

registry.category("web_tour.tours").add("website_sale_cart_offcanvas_stay", {
    url: "/shop",
    steps: () => [
        ...tourUtils.addToCart({ productName: "Offcanvas Product" }),
        {
            content: "The standard notification shows up",
            trigger: '.toast a[href="/shop/cart"]:contains("View cart")',
        },
        {
            content: "No panel was added to the page",
            trigger: "body:not(:has(#o_wsale_cart_offcanvas))",
        },
    ],
});
