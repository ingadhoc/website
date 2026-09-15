import { browser } from "@web/core/browser/browser";

export function getCartOffcanvasEl() {
    return document.getElementById("o_wsale_cart_offcanvas");
}

/**
 * Whether the current page is the cart page.
 *
 * Checked on the DOM and not on the URL: with a language prefix the path is `/es/shop/cart`.
 */
export function isCartPage() {
    return !!document.getElementById("shop_cart");
}

/**
 * Update the cart counter in the header.
 *
 * `wSaleUtils.updateCartNavBar` cannot be reused here: it dereferences `.oe_cart`, which only
 * exists on the checkout pages, and drops the rendered HTML when there is no `.js_cart_lines`.
 */
export function updateCartIcon(cartQuantity) {
    browser.sessionStorage.setItem("website_sale_cart_quantity", cartQuantity);
    for (const quantityEl of document.querySelectorAll(".my_cart_quantity")) {
        quantityEl.classList.toggle("d-none", !cartQuantity);
        quantityEl.textContent = cartQuantity;
    }
    if (cartQuantity) {
        document.querySelector("li.o_wsale_my_cart")?.classList.remove("d-none");
    }
}
