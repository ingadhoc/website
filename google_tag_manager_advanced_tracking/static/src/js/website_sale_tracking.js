/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";


const PaymentForm = publicWidget.registry.PaymentForm;


publicWidget.registry.GoogleTagManagerAdvancedTracking = publicWidget.Widget.extend({
    selector: '.oe_website_sale',
    events: {
    'click #add_to_cart': '_onClickAddToCartProduct',
    'click a.add_to_cart_products_item': '_onClickAddToCartProductsItem',
    'click a.on_checkout_start_js': '_onCheckoutStartJs',
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
        var product_price = dataTarget.dataset.product_price;
        var product_amount = $("[name=add_qty]").val();
        var amount = parseFloat(product_price * product_amount).toFixed(2);
        const dict = {
            'event': 'add_to_cart',
            'value': amount,
            'items': [{
                'item_name': product_name,
                'item_id': product_id,
                'price': product_price
            }]
        }
        this._pushInfo(dict);
    },
    _onClickAddToCartProductsItem: function(ev) {
        var dataTarget = ev.target.closest('div.o_wsale_product_btn');
        var product_id = dataTarget.dataset.product_id;
        var product_sku = dataTarget.dataset.product_sku;
        var product_name = dataTarget.dataset.product_name;
        var product_price = dataTarget.dataset.product_price;
        const dict = {
            'event': 'add_to_cart',
            'value': product_price,
            'items': {
                'item_name': product_name,
                'item_id': product_sku || product_id,
                'price': product_price
            }
        }
        this._pushInfo(dict);
    },
    _onCheckoutStartJs: function () {
        var dataTarget = $("#cart_products")[0];
        const info = dataTarget.dataset.cart_info;
        const dict = {
            'event':'begin_checkout',
            'ecommerce':{'items':info}
        }
        this._pushInfo(dict);
    },
});

//Heredamos PaymentForm form porque el metodo _submitForm tiene stopPropagation y preventDefault, impidiendonos hacerlo en el widget GoogleTagManagerAdvancedTracking
PaymentForm.include({
    _pushInfo: function (dict){
        if(typeof(dataLayer) !== 'undefined'){
            dataLayer.push(dict);
            console.log(dict);
        }
    },
    // @override
    _submitForm: async function (ev) {
        const info = $("#o_wsale_accordion_item")[0].dataset.purchase_info;
        const dict = {
            'event':'purchase',
            'ecommerce':info
        }
        this._pushInfo(dict);
        this._super(...arguments);
    },
})

