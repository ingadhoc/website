/** @odoo-module **/

import { PaymentForm } from '@payment/interactions/payment_form';
import { cookie } from "@web/core/browser/cookie";
import { registry } from '@web/core/registry';
import { patch } from '@web/core/utils/patch';
import { Interaction } from '@web/public/interaction';
import { Form } from "@website/snippets/s_website_form/form";
import { WebsiteSale } from '@website_sale/interactions/website_sale';


export class GoogleTagManagerAdvancedTracking extends Interaction {
    static selector = "#wrapwrap";

    dynamicContent = {
        '#add_to_cart': { 't-on-click': this.onClickAddToCartProduct },
        'button.add_to_cart_products_item': { 't-on-click': this.onClickAddToCartProductsItem },
        'a.on_checkout_start_js': { 't-on-click': this.onCheckoutStartJs },
        '.s_website_form_rows': { 't-on-click': this.onFormStart },
    };

    start() {
        //push cart_view info when DOM loaded in /shop/cart
        this.cart_page = this.el.querySelector(".js_cart_lines");
        if (this.cart_page) {
            this.cart_element = this.el.querySelector("#cart_main_button");
            this.onCartView(this.cart_element);
        }
        //push purchase info when DOM loaded in /shop/confirmation
        this.confirmation_page = document.querySelector("[name=order_confirmation]");
        if (this.confirmation_page) {
            this.confirmation = this.el.querySelector('.o_website_sale_checkout_container')
            this.onPurchaseConfirm(this.confirmation);
        }
        //push view_item info when DOM loaded in /shop/[product]
        this.product_details = this.el.querySelector('div#product_details');
        if (this.product_details) {
            this.onViewItem(this.product_details);
        }
    }

    _pushInfo(dict) {
        if (typeof (dataLayer) !== 'undefined') {
            dataLayer.push(dict);
            console.log(dict);
        }
    }

    onClickAddToCartProduct(ev) {
        const dataTarget = ev.target.closest('a#add_to_cart');
        const product_id = dataTarget.dataset.product_id;
        const product_sku = dataTarget.dataset.product_sku;
        const product_name = dataTarget.dataset.product_name;
        const currency = dataTarget.dataset.currency;
        const product_price = dataTarget.dataset.product_price;
        const product_amount = document.querySelector("[name=add_qty]").value;
        const amount = parseFloat(product_price * product_amount).toFixed(2);
        const dict = {
            'event': 'add_to_cart',
            'ecommerce': {
                'currency': currency,
                'value': amount,
                'items': [{
                    'item_name': product_name,
                    'item_id': product_sku || product_id,
                    'price': product_price,
                    'quantity': product_amount,
                }]
            }
        }
        this._pushInfo(dict);
    }

    onClickAddToCartProductsItem(ev) {
        const dataTarget = ev.target.closest('div.o_wsale_product_btn');
        const product_id = dataTarget.dataset.product_id;
        const currency = dataTarget.dataset.currency;
        const product_sku = dataTarget.dataset.product_sku;
        const product_name = dataTarget.dataset.product_name;
        const product_price = dataTarget.dataset.product_price;
        const dict = {
            'event': 'add_to_cart',
            'ecommerce': {
                'value': product_price,
                'currency': currency,
                'items': {
                    'item_name': product_name,
                    'item_id': product_sku || product_id,
                    'price': product_price,
                }
            }
        }
        this._pushInfo(dict);
    }

    onCheckoutStartJs(ev) {
        const dataTarget = document.querySelector("#cart_products");
        if( dataTarget && Object.keys(dataTarget.dataset).length > 0) {
            try {
                const currency = dataTarget.dataset.currency;
                const value = dataTarget.dataset.value;
                const info_string = dataTarget.dataset.cart_info;

                const info = JSON.parse(info_string || '[]');
                const allLines = Array.isArray(info) ? info : (info.items || []);
                const rewardTotal = allLines
                    .filter((line) => line && line.is_reward_line)
                    .reduce((sum, line) => {
                        const price = Number(line.price || 0);
                        const quantity = Number(line.quantity || 1);
                        return sum + (price * quantity);
                    }, 0);
                const items = allLines
                    .filter((line) => line && !line.is_reward_line)
                    .map((line) => ({
                        item_name: line.item_name,
                        item_id: line.item_id,
                        price: line.price,
                        quantity: line.quantity,
                    }));
                const dict = {
                    'event':'begin_checkout',
                    'ecommerce':{
                        'currency': currency,
                        'value': Number(value || 0),
                        'discount': Math.abs(rewardTotal),
                        'items': items,
                    }
                }
                this._pushInfo(dict);
            } catch (e) {
                console.error("GTM Error: Failed to parse cart_info in _onCheckoutStartJs.", e);
                console.error("GTM Debug: Original cart_info string:", document.querySelector("#cart_products")?.dataset.cart_info);
            }
        }
    }
    onCartView(element) {
        try {
            if(element){
                 const info_string = element.dataset.cart_info;
                const info = JSON.parse(info_string || '{}');
                const dict = {
                    'event': 'view_cart',
                    'ecommerce': info
                }
                this._pushInfo(dict);
            }
        } catch (e) {
            console.error("GTM Error: Failed to parse cart_info in _onCartView.", e);
            console.error("GTM Debug: Original cart_info string:", element?.dataset.cart_info);
        }
    }
    onPurchaseConfirm(confirmation) {
        try {
            const info_string = confirmation.dataset.purchase_info;

            // jQuery .data() auto-parses valid JSON into an object, handle both cases
            let info;
            if (typeof info_string === 'object') {
                info = info_string;
            } else {
                let jsonString = info_string.replace(/\\/g, '\\\\').replace(/\'/g, '"');
                jsonString = jsonString.replace(/:\s*None([,\}])/g, ': null$1');
                jsonString = jsonString.replace(/:\s*True([,\}])/g, ': true$1');
                jsonString = jsonString.replace(/:\s*False([,\}])/g, ': false$1');
                info = JSON.parse(jsonString);
            }
            const dict = {
                'event': 'purchase',
                'ecommerce': info
            }
            this._pushInfo(dict)
        } catch (e) {
            console.error("GTM Error: Failed to parse purchase_info in _onPurchaseConfirm.", e);
            console.error("GTM Debug: Original purchase_info string:", confirmation?.dataset.purchase_info);
        }
    }
    onFormStart(ev) {
        const formStarted = cookie.get("form_start_sent");
        if (formStarted) {
            // no hacer nada
        } else {
            const dataTarget = ev.target.closest("form");
            const form_name = dataTarget.id;
            const form_destination = dataTarget.dataset.model_name;
            const dict = {
                'event': 'form_start',
                'ecommerce': {
                    'form_name': form_name,
                    'form_destination': form_destination
                }
            }
            cookie.set("form_start_sent", true, 600);
            this._pushInfo(dict)
        }
    }

    onViewItem(product_details) {
        const product_id = product_details.dataset.product_id;
        const currency = product_details.dataset.currency;
        const product_sku = product_details.dataset.product_sku;
        const product_name = product_details.dataset.product_name;
        const product_price = product_details.dataset.product_price;
        const dict = {
            'event': 'view_item',
            'ecommerce': {
                'currency': currency,
                'value': product_price,
                'items': {
                    'item_id': product_sku || product_id,
                    'item_name': product_name,
                    'price': product_price,
                }
            }
        }
        this._pushInfo(dict);
    }
}

patch(WebsiteSale.prototype, {
    _pushInfo(dict) {
        if (typeof (dataLayer) !== 'undefined') {
            dataLayer.push(dict);
            console.log(dict);
        }
    },
    // @override
    onSubmitSaleSearch(ev) {
        const search_term = ev.target.value;
        const dict = {
            'event': 'search',
            'ecommerce': {
                'search_term': search_term
            }
        };
        this._pushInfo(dict);
        super.onSubmitSaleSearch(...arguments);
    }
});

patch(Form.prototype, {
    _pushInfo(dict) {
        if (typeof (dataLayer) !== 'undefined') {
            dataLayer.push(dict);
            console.log(dict);
        }
    },

    // @override
    async send(e){
        const dataTarget = e.target.closest("form");
        const form_name = dataTarget.id;
        const form_destination = dataTarget.dataset.model_name;
        const dict = {
            'event': 'form_submit',
            'ecommerce': {
                'form_name': form_name,
                'form_destination': form_destination
            }
        };
        this._pushInfo(dict);
        super.send(...arguments);
    }
});


patch(PaymentForm.prototype, {
    _pushInfo(dict) {
        if (typeof (dataLayer) !== 'undefined') {
            dataLayer.push(dict);
            console.log(dict);
        }
    },

    // @override
    async submitForm(ev) {
        // Start Payment Event
        try {
            const info_div = document.querySelector(".o_website_sale_checkout_container");
            if (info_div) {
                const info_string = info_div.dataset.purchase_info;
                const payment_method_input = document.querySelector('#payment_method input[type="radio"]:checked');
                const sale_id = document.querySelector(".my_cart_quantity")?.dataset.orderId;

                const parsed_info = JSON.parse(info_string || '{}');
                const payment_info = {
                    'currency': parsed_info.currency,
                    'value': parsed_info.value,
                    'transaction_id': sale_id,
                    'payment_type': payment_method_input.dataset.providerCode
                }
                const payment_dict = {
                    'event': 'start_payment',
                    'ecommerce': payment_info
                }
                this._pushInfo(payment_dict);
            }
        } catch (e) {
            console.error("GTM Error: Failed to parse purchase_info in _onClickPay.", e);
            console.error("GTM Debug: Original purchase_info string:", document.querySelector(".o_website_sale_checkout_container")?.dataset.purchase_info);
    }
        // Start Payment Event
        super.submitForm(...arguments);
    },
});


registry.category('public.interactions').add('google_tag_manager_advanced_tracking.GoogleTagManagerAdvancedTracking', GoogleTagManagerAdvancedTracking);
