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
        const product_name = dataTarget.dataset.product_name;
        const product_price = dataTarget.dataset.product_price;
        const product_amount = document.querySelector("[name=add_qty]").value;
        const amount = parseFloat(product_price * product_amount).toFixed(2);
        const dict = {
            'content_name': product_name,
            'content_ids': [product_id],
            'content_type': 'product',
            'value': product_price,
            'total': amount,
        }
        this._pushInfo('AddToCart', dict);
    }

    onClickAddToCartProductsItem(ev) {
        const dataTarget = ev.target.closest('div.o_wsale_product_btn');
        const product_id = dataTarget.dataset.product_id;
        const product_sku = dataTarget.dataset.product_sku;
        const product_name = dataTarget.dataset.product_name;
        const product_price = dataTarget.dataset.product_price;
        const dict = {
            'content_name': product_name,
            'content_ids': [product_sku || product_id],
            'content_type': 'product',
            'value': product_price,
        }
        this._pushInfo('AddToCart', dict);
    }

    onCheckoutStartJs(ev) {
        // Solo ejecutar si estamos en la página del carrito
        const currentStep = ev.target.dataset.current_website_checkout_step_href;
        if (currentStep !== '/shop/cart') {
            return;
        }
        const dataTarget = document.getElementById("cart_products");
        const info = dataTarget.dataset.cart_info;
        const dict = {
            'event':'begin_checkout',
            'ecommerce':{'items':info}
        }
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
        if(info_div){
            const info = info_div.dataset.purchase_info;
            const dict = {
                'event':'purchase',
                'ecommerce':info
            }
            this._pushInfo('Purchase', dict);
        }
        super.submitForm(...arguments);
    },
})

registry.category('public.interactions').add('facebook_pixel_tracking.FacebookPixelTracking', FacebookPixelTracking);
