odoo.define("google_tag_manager_advanced_tracking.tracking", function (require) {
    "use strict";

    const publicWidget = require("web.public.widget");
    const PaymentCheckoutForm = publicWidget.registry.PaymentCheckoutForm;
    const {getCookie, setCookie} = require('web.utils.cookies');

    publicWidget.registry.GoogleTagManagerAdvancedTracking = publicWidget.Widget.extend({
        selector: '#wrapwrap',
        events: {
        'click #add_to_cart': '_onClickAddToCartProduct',
        'click a.add_to_cart_products_item': '_onClickAddToCartProductsItem',
        'click a.on_checkout_start_js': '_onCheckoutStartJs',
        "click .s_website_form_rows": "_onFormStart",
        },

        start: function () {
            //push cart_view info when DOM loaded in /shop/cart
            var cart_page = $(".js_cart_lines");
            if(cart_page.length){
                const cart_element = $("#cart_main_button");
                this._onCartView(cart_element)
            }
            //push purchase info when DOM loaded in /shop/confirmation
            const $confirmation = $('div.oe_website_sale_tx_status');
            if($confirmation.length){
                this._onPurchaseConfirm($confirmation)
            }
            //push view_item info when DOM loaded in /shop/[product]
            const $product_details = $('div#product_details')
            if($product_details.length){
                this._onViewItem($product_details)
            }
        },

        _pushInfo: function (dict){
            if(typeof(dataLayer) !== 'undefined'){
                dataLayer.push(dict);
                console.log(dict);
            }
        },
        _onClickAddToCartProduct: function (ev){
            var dataTarget = ev.target.closest('a#add_to_cart');
            var product_id = dataTarget.dataset.product_id;
            var product_name = dataTarget.dataset.product_name;
            var currency = dataTarget.dataset.currency;
            var product_price = dataTarget.dataset.product_price;
            var product_amount = $("[name=add_qty]").val();
            var amount = parseFloat(product_price * product_amount).toFixed(2);
            const dict = {
                'event': 'add_to_cart',
                'ecommerce': {
                    'currency': currency,
                    'value': amount,
                    'items': [{
                        'item_name': product_name,
                        'item_id': product_id,
                        'price': product_price,
                        'quantity': product_amount,
                    }]
                }
            }
            this._pushInfo(dict);
        },
        _onClickAddToCartProductsItem: function(ev) {
            var dataTarget = ev.target.closest('div.o_wsale_product_btn');
            var product_id = dataTarget.dataset.product_id;
            var currency = dataTarget.dataset.currency;
            var product_sku = dataTarget.dataset.product_sku;
            var product_name = dataTarget.dataset.product_name;
            var product_price = dataTarget.dataset.product_price;
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
        },
        _onCheckoutStartJs: function () {
            var dataTarget = $("#cart_products")[0];
            var currency = dataTarget.dataset.currency;
            var value = dataTarget.dataset.value;
            const info = dataTarget.dataset.cart_info;
            const dict = {
                'event':'begin_checkout',
                'ecommerce':{
                    'currency': currency,
                    'value': value,
                    'items':info
                }
            }
            this._pushInfo(dict);
        },

        _onViewItem : function(product_details) {
            var product_id = product_details[0].dataset.product_id;
            var currency = product_details[0].dataset.currency;
            var product_sku = product_details[0].dataset.product_sku;
            var product_name = product_details[0].dataset.product_name;
            var product_price = product_details[0].dataset.product_price;
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
        },
        _onCartView: function(element){
            const info = element[0].dataset.cart_info;
            const dict = {
                'event': 'view_cart',
                'ecommerce': info
            }
            this._pushInfo(dict);

        },
        _onPurchaseConfirm: function(confirmation) {
            const info = confirmation.data('purchase_info');
            const dict = {
                'event': 'purchase',
                'ecommerce': info
            }
            this._pushInfo(dict)
        },
        _onFormStart: function(ev){
            var cookie = getCookie('form_start_sent');
            if(cookie){
                // no hacer nada
            }else{
                const dataTarget = ev.target.closest("form")
                const form_name = dataTarget.id;
                const form_destination = dataTarget.dataset.model_name
                const dict = {
                    'event': 'form_start',
                    'ecommerce': {
                        'form_name': form_name,
                        'form_destination': form_destination
                    }
                }
                setCookie('form_start_sent', true, 600, 'required');
                this._pushInfo(dict)
            }
        },
    });

    //Heredamos payment checkout form porque el metodo _onClickPay tiene stopPropagation y preventDefault, impidiendonos hacerlo en el widget GoogleTagManagerAdvancedTracking
    PaymentCheckoutForm.include({
        _pushInfo: function (dict){
            if(typeof(dataLayer) !== 'undefined'){
                dataLayer.push(dict);
                console.log(dict);
            }
        },
        // @override
        _onClickPay: async function (ev) {
            // Start Payment Event
            const info = $(".toggle_summary_div")[0].dataset.purchase_info;
            const payment_method_input = document.querySelector('#payment_method input[type="radio"]:checked');
            const sale_id = $(".my_cart_quantity")[0].dataset.orderId
            const parsed_info = JSON.parse(info.replace(/'/g, '"'))
            const payment_info = {
                'currency': parsed_info.currency,
                'value': parsed_info.value,
                'transaction_id': sale_id,
                'payment_type': payment_method_input.dataset.provider
            }
            const payment_dict = {
                'event': 'start_payment',
                'ecommerce': payment_info
            }
            this._pushInfo(payment_dict);
            // Start Payment Event

            this._super(...arguments);
        },
    })

    return publicWidget.registry.GoogleTagManagerAdvancedTracking;
});
