/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";


const PaymentForm = publicWidget.registry.PaymentForm;

publicWidget.registry.FacebookPixelTracking = publicWidget.Widget.extend({
    selector: '.oe_website_sale',
    events: {
    "click #add_to_cart": "_onClickAddToCartProduct",
    "click a.add_to_cart_products_item": "_onClickAddToCartProductsItem",
    "click a.on_checkout_start_js": "_onCheckoutStartJs",
    },

    _pushInfo: function (event, dict) {
        if (typeof fbq !== 'undefined') {
            fbq('track', event, dict);
        }
        console.log(event,dict);
    },

    _onClickAddToCartProduct: function (ev) {
        var dataTarget = ev.target.closest('a#add_to_cart');
        var product_id = dataTarget.dataset.product_id;
        var product_sku = dataTarget.dataset.product_sku;
        var product_name = dataTarget.dataset.product_name;
        var product_price = parseFloat(dataTarget.dataset.product_price) || 0;
        var currency = dataTarget.dataset.currency;
        const dict = {
            content_name: product_name,
            content_ids: [String(product_sku || product_id)],
            content_type: 'product',
            value: product_price,
            currency: currency,
        };
        this._pushInfo('AddToCart', dict);
    },

    _onClickAddToCartProductsItem: function (ev) {
        var dataTarget = ev.target.closest('div.o_wsale_product_btn');
        var product_id = dataTarget.dataset.product_id;
        var product_sku = dataTarget.dataset.product_sku;
        var product_name = dataTarget.dataset.product_name;
        var product_price = parseFloat(dataTarget.dataset.product_price) || 0;
        const dict = {
            content_name: product_name,
            content_ids: [String(product_sku || product_id)],
            content_type: 'product',
            value: product_price,
        };
        this._pushInfo('AddToCart', dict);
    },

    _onCheckoutStartJs: function () {
        var dataTarget = $("#cart_products")[0];
        const items = JSON.parse(dataTarget.dataset.cart_info || '[]');
        const contents = items
            .filter(item => !item.is_reward_line)
            .map(item => ({
                id: String(item.item_id),
                quantity: item.quantity,
                item_price: item.price,
            }));
        if (!contents.length) {
            return;
        }
        const dict = {
            content_ids: contents.map(item => item.id),
            content_type: 'product',
            contents: contents,
            num_items: contents.length,
            value: parseFloat(dataTarget.dataset.value) || 0,
            currency: dataTarget.dataset.currency,
        };
        this._pushInfo('InitiateCheckout', dict);
    },
});

// Heredamos PaymentForm porque el método _submitForm tiene stopPropagation y preventDefault,
// impidiéndonos capturarlo desde el widget FacebookPixelTracking.
PaymentForm.include({

    _pushInfo: function (event, dict) {
        if (typeof fbq !== 'undefined') {
            fbq('track', event, dict);
        }
    },

    // @override
    _submitForm: async function (ev) {
        const info_div = $("#o_wsale_accordion_item")[0];
        if (info_div) {
            const info = JSON.parse(info_div.dataset.purchase_info || '{}');
            const contents = (info.items || []).map(item => ({
                id: String(item.item_id),
                quantity: item.quantity,
                item_price: item.price,
            }));
            const dict = {
                value: info.value,
                currency: info.currency,
                content_ids: contents.map(item => item.id),
                contents: contents,
                content_type: 'product',
            };
            this._pushInfo('Purchase', dict);
        }
        await this._super(...arguments);
    },
})
