 /** @odoo-module **/

import { PaymentForm } from '@payment/interactions/payment_form';
import { registry } from '@web/core/registry';
import { patch } from '@web/core/utils/patch';
import { Interaction } from '@web/public/interaction';

export class FacebookPixelTracking extends Interaction {
    static selector = ".oe_website_sale";

    dynamicContent = {
        '#add_to_cart': { 't-on-click': this.onClickAddToCartProduct },
        'button.add_to_cart_products_item': { 't-on-click': this.onClickAddToCartProductsItem },
        'a.on_checkout_start_js': { 't-on-click': this.onCheckoutStartJs },
    };

     _pushInfo(event, dict){
        if(typeof(fbq) !== 'undefined'){
            fbq('track', event, dict);
            console.log(dict);
        }
    }

    onClickAddToCartProduct(ev){
        const dataTarget = ev.target.closest('a#add_to_cart');
        const product_id = dataTarget.dataset.product_id;
        const product_sku = dataTarget.dataset.product_sku;
        const product_name = dataTarget.dataset.product_name;
        const product_price = parseFloat(dataTarget.dataset.product_price) || 0;
        const currency = dataTarget.dataset.currency;
        const dict = {
            content_name: product_name,
            content_ids: [String(product_sku || product_id)],
            content_type: 'product',
            value: product_price,
            currency: currency,
        };
        this._pushInfo('AddToCart', dict);
    }

    onClickAddToCartProductsItem(ev) {
        const dataTarget = ev.target.closest('div.o_wsale_product_btn');
        const product_id = dataTarget.dataset.product_id;
        const product_sku = dataTarget.dataset.product_sku;
        const product_name = dataTarget.dataset.product_name;
        const product_price = parseFloat(dataTarget.dataset.product_price) || 0;
        const dict = {
            content_name: product_name,
            content_ids: [String(product_sku || product_id)],
            content_type: 'product',
            value: product_price,
        };
        this._pushInfo('AddToCart', dict);
    }

    onCheckoutStartJs(ev) {
        // Solo ejecutar si estamos en la página del carrito
        const currentStep = ev.target.dataset.current_website_checkout_step_href;
        if (currentStep !== '/shop/cart') {
            return;
        }
        const dataTarget = document.getElementById("cart_products");
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
    }

}


//Heredamos PaymentForm form porque el metodo _submitForm tiene stopPropagation y preventDefault, impidiendonos hacerlo en el widget GoogleTagManagerAdvancedTracking

patch(PaymentForm.prototype, {

    _pushInfo(event, dict){
        if(typeof(fbq) !== 'undefined'){
            fbq('track', event, dict);
            console.log(dict);
        }
    },


    // @override
    async submitForm(ev) {
        const info_div = document.querySelector(".o_website_sale_checkout_container");
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
        super.submitForm(...arguments);
    },
})

registry.category('public.interactions').add('facebook_pixel_tracking.FacebookPixelTracking', FacebookPixelTracking);
