/** @odoo-module **/
/**
 * GA4 Ecommerce Tracking
 *
 * Extends the native Odoo 19 website_sale Tracking interaction
 * (which already handles view_item, add_to_cart and purchase) with
 * the events that are not yet covered natively:
 *
 *   view_cart        – cart page loaded
 *   begin_checkout   – user clicks "Proceed to Checkout"
 *   add_shipping_info – user selects a delivery method
 *   add_payment_info – user submits the payment form
 *   remove_from_cart – user decrements qty or deletes a cart line
 *   search           – (extends native VPV with proper GA4 search event)
 *
 * Events view_item, add_to_cart and purchase are intentionally NOT
 * re-implemented here – Odoo 19's native tracking.js already fires them
 * via window.gtag using the CustomEvents dispatched by variant_mixin.js
 * and cart_service.js.
 */

import { PaymentForm } from '@payment/interactions/payment_form';
import { registry } from '@web/core/registry';
import { patch } from '@web/core/utils/patch';
import { Interaction } from '@web/public/interaction';
import { CartLine } from '@website_sale/interactions/cart_line';
import { Tracking } from '@website_sale/interactions/tracking';

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/**
 * Forward a GA4 event via the native gtag function injected by Odoo.
 * Silently no-ops when gtag is not available (e.g. ad-blocker or missing key).
 *
 * @param {string} name  GA4 event name
 * @param {Object} params  GA4 event parameters
 */
function _trackGa4(name, params) {
    const ga = window.gtag;
    if (typeof ga === 'function') {
        ga('event', name, params);
        // eslint-disable-next-line no-console
        console.debug('[GA4]', name, params);
    }
}

/**
 * Parse the JSON stored in a dataset attribute.
 * Returns null on error rather than throwing.
 *
 * @param {string|undefined} raw
 * @returns {any|null}
 */
function _parseJson(raw) {
    if (!raw) return null;
    try {
        return JSON.parse(raw);
    } catch (e) {
        console.error('[GA4] JSON parse error:', e, '\nRaw value:', raw);
        return null;
    }
}

/**
 * Fire remove_from_cart for a given cart product element.
 *
 * @param {HTMLElement} cartProductEl  .o_cart_product div
 * @param {number} removedQty  quantity being removed
 */
function _fireRemoveFromCart(cartProductEl, removedQty) {
    if (!cartProductEl) return;
    const ds = cartProductEl.dataset;
    const currency = ds.currency || '';
    const price = parseFloat(ds.productPrice || 0);
    const itemId = ds.productSku || ds.productId || '';
    const itemName = ds.productName || '';
    const qty = removedQty > 0 ? removedQty : 1;

    _trackGa4('remove_from_cart', {
        currency,
        value: price * qty,
        items: [{
            item_id: itemId,
            item_name: itemName,
            price,
            quantity: qty,
        }],
    });
}

// ---------------------------------------------------------------------------
// Main GA4 Ecommerce Interaction
// ---------------------------------------------------------------------------

export class GA4EcommerceTracking extends Interaction {
    static selector = '.oe_website_sale';

    dynamicContent = {
        /** Delivery method radio – fires add_shipping_info on selection */
        '[name="o_delivery_radio"]': {
            't-on-change': this.onDeliverySelect,
        },
    };

    setup() {
        // view_cart: fires once on the cart page
        if (this.el.querySelector('.js_cart_lines')) {
            this._fireViewCart();
        }
    }

    // ------------------------------------------------------------------
    // view_cart
    // ------------------------------------------------------------------

    _fireViewCart() {
        const cartProductsEl = this.el.querySelector('#cart_products');
        if (!cartProductsEl) return;
        const items = _parseJson(cartProductsEl.dataset.cartInfo);
        if (!items) return;
        _trackGa4('view_cart', {
            currency: cartProductsEl.dataset.currency || '',
            value: parseFloat(cartProductsEl.dataset.value || 0),
            items,
        });
    }

    // ------------------------------------------------------------------
    // add_shipping_info
    // ------------------------------------------------------------------

    onDeliverySelect(ev) {
        const radio = ev.target;
        if (!radio.matches('[name="o_delivery_radio"]')) return;

        // Carrier name lives in the sibling label → span[name="o_delivery_method_name"]
        const label = this.el.querySelector(
            `label[for="${radio.id}"] [name="o_delivery_method_name"]`
        );
        const shippingTier = label ? label.textContent.trim() : radio.dataset.dmId || '';

        // Purchase info (items, value, currency) from checkout container
        const container = this.el.querySelector('.o_website_sale_checkout_container');
        const purchaseInfo = container
            ? _parseJson(container.dataset.purchaseInfo)
            : null;

        _trackGa4('add_shipping_info', {
            currency: purchaseInfo ? purchaseInfo.currency : '',
            value: purchaseInfo ? purchaseInfo.value : 0,
            shipping_tier: shippingTier,
            items: purchaseInfo ? (purchaseInfo.items || []) : [],
        });
    }
}

registry
    .category('public.interactions')
    .add('ga4_ecommerce.GA4EcommerceTracking', GA4EcommerceTracking);

// ---------------------------------------------------------------------------
// Patch: Tracking – begin_checkout
// Extends the native onCheckoutStart VPV to also fire the proper GA4 event.
// ---------------------------------------------------------------------------

patch(Tracking.prototype, {
    onCheckoutStart(ev) {
        // Fire proper begin_checkout event with cart data
        try {
            const cartProductsEl = document.querySelector('#cart_products');
            if (cartProductsEl) {
                const items = _parseJson(cartProductsEl.dataset.cartInfo);
                if (items) {
                    _trackGa4('begin_checkout', {
                        currency: cartProductsEl.dataset.currency || '',
                        value: parseFloat(cartProductsEl.dataset.value || 0),
                        items,
                    });
                }
            }
        } catch (e) {
            console.error('[GA4] begin_checkout error:', e);
        }
        // Always call the native implementation (fires the VPV)
        super.onCheckoutStart(ev);
    },
});

// ---------------------------------------------------------------------------
// Patch: PaymentForm – add_payment_info
// Fires before the payment provider's submitForm() logic runs.
// ---------------------------------------------------------------------------

patch(PaymentForm.prototype, {
    async submitForm(ev) {
        try {
            const container = document.querySelector('.o_website_sale_checkout_container');
            if (container) {
                const purchaseInfo = _parseJson(container.dataset.purchaseInfo);
                if (purchaseInfo) {
                    const selectedProvider = document.querySelector(
                        '#payment_method input[name="o_payment_radio"]:checked'
                    );
                    _trackGa4('add_payment_info', {
                        currency: purchaseInfo.currency || '',
                        value: purchaseInfo.value || 0,
                        payment_type: selectedProvider
                            ? (selectedProvider.dataset.providerCode || '')
                            : '',
                        items: purchaseInfo.items || [],
                    });
                }
            }
        } catch (e) {
            console.error('[GA4] add_payment_info error:', e);
        }
        return super.submitForm(...arguments);
    },
});

// ---------------------------------------------------------------------------
// Patch: CartLine – remove_from_cart
// Captures quantity decrements and explicit deletions before the RPC fires
// (the page may redirect immediately after deletion, so we fire the event
// before calling super).
// ---------------------------------------------------------------------------

patch(CartLine.prototype, {
    /**
     * Override: fire remove_from_cart when the minus button is clicked
     * and the quantity will drop (BEFORE calling super so the event
     * fires even if the page redirects on full removal).
     */
    async incOrDecQuantity(ev, currentTargetEl) {
        try {
            const isDecrement = currentTargetEl
                .querySelector('i')
                ?.classList.contains('oi-minus');
            if (isDecrement) {
                const input = currentTargetEl
                    .closest('.css_quantity')
                    ?.querySelector('input.js_quantity');
                const currentQty = parseFloat(input?.value || 0);
                if (currentQty > 0) {
                    const cartProduct = currentTargetEl.closest('.o_cart_product');
                    _fireRemoveFromCart(cartProduct, 1);
                }
            }
        } catch (e) {
            console.error('[GA4] remove_from_cart (inc/dec) error:', e);
        }
        return super.incOrDecQuantity(ev, currentTargetEl);
    },

    /**
     * Override: fire remove_from_cart for the full line quantity when
     * the delete button is clicked (BEFORE calling super).
     */
    async deleteProduct(ev) {
        try {
            const cartProduct = ev.currentTarget.closest('.o_cart_product');
            const input = cartProduct?.querySelector('.css_quantity > input.js_quantity');
            const qty = parseFloat(input?.value || 0);
            if (qty > 0) {
                _fireRemoveFromCart(cartProduct, qty);
            }
        } catch (e) {
            console.error('[GA4] remove_from_cart (delete) error:', e);
        }
        return super.deleteProduct(ev);
    },
});
