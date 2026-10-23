/** @odoo-module **/

import { registry } from '@web/core/registry';
import { Interaction } from '@web/public/interaction';

/**
 * Meta Pixel browser events, built on the tracking data website_sale already
 * publishes: the `add_to_cart_event` it dispatches and the `#cart_tracking_info`
 * element it renders on the cart page. Nothing here reads the product DOM, so
 * variants, combos and reward lines come out of the core, already resolved.
 */
export class FacebookPixelTracking extends Interaction {
    static selector = '.oe_website_sale';

    dynamicContent = {
        'a[href^="/shop/checkout"]': { 't-on-click': this.onCheckoutStart },
        _root: {
            't-on-add_to_cart_event': (ev) => this.onAddToCart(ev),
            // Raising the quantity from the cart page goes through this one.
            't-on-update_cart_event': (ev) => this.onAddToCart(ev),
        },
    };

    _track(event, data) {
        if (typeof fbq !== 'undefined') {
            fbq('track', event, data);
        }
    }

    /**
     * Meta's `value` is what the customer pays. The core publishes prices net
     * of tax because that is what GA4 expects, so the module adds
     * `price_taxinc` to every item server-side.
     */
    _toContents(items) {
        return items.map((item) => ({
            id: String(item.item_id),
            quantity: item.quantity,
            item_price: item.price_taxinc ?? item.price,
        }));
    }

    _buildPayload(contents, currency) {
        return {
            content_ids: contents.map((item) => item.id),
            content_type: 'product',
            contents: contents,
            num_items: contents.length,
            value: contents.reduce((total, item) => total + item.item_price * item.quantity, 0),
            currency: currency,
        };
    }

    onAddToCart(ev) {
        const { currency, items } = ev.detail;
        // update_cart_event also fires when a line shrinks, and then
        // delta_quantity is negative: Meta has no event for removing.
        const added = (items || []).filter((item) => (item.delta_quantity ?? 1) > 0);
        if (!added.length) {
            return;
        }
        this._track('AddToCart', this._buildPayload(this._toContents(added), currency));
    }

    onCheckoutStart() {
        const raw = this.el.querySelector('#cart_tracking_info')?.dataset?.cartTrackingInfo;
        if (!raw) {
            return;
        }
        let info;
        try {
            info = JSON.parse(raw);
        } catch {
            return;
        }
        const contents = this._toContents(info.items || []);
        if (!contents.length) {
            return;
        }
        this._track('InitiateCheckout', this._buildPayload(contents, info.currency));
    }
}

// The Purchase event is not emitted from the browser: it is sent server-side
// via the Meta Conversions API at sale.order confirmation (see
// models/sale_order.py). This keeps a single source of truth and avoids
// reporting purchases for carts that fail or are abandoned at the gateway.

registry
    .category('public.interactions')
    .add('facebook_pixel_tracking.FacebookPixelTracking', FacebookPixelTracking);
