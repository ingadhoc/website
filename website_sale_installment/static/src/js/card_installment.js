odoo.define('website_sale_installment.installment_popup', function (require) {
    'use strict';


    var core = require('web.core');
    var publicWidget = require('web.public.widget');
    const Dialog = require('web.Dialog');
    var utils = require('web.utils');
    var website_sale_utils = require('website_sale.utils');
    var VariantMixin = require('sale.VariantMixin');

    var qweb = core.qweb;
    var _t = core._t;
    publicWidget.registry.installmentPopup = publicWidget.Widget.extend( {
        xmlDependencies: ['/website_sale_installment/static/src/xml/card_installment.xml'],
        //template: 'website_sale_installment.instalment_popup',
        selector: '.js_card',
        init: function () {
            this._super.apply(this, arguments);
        },
        events: {
            'change .card': '_onChangeCardSelector',
            'click .o_installment_button': '_openInstallmentPopUp',
        },
        _openInstallmentPopUp: function(event){
            let product_product_id = document.querySelector('input.product_id').value;
            let product_template_id = document.querySelector('input.product_template_id').value;
            var self = this;
            this._rpc({
                route: '/installment_prices',
                params: {
                    product_tmpl: product_template_id,
                    product: product_product_id,
                },
            }).then(function (data) {
                let content = $(qweb.render('website_sale_installment.instalment_popup', {
                    installment_tree: data,
                    _priceToStr: VariantMixin._priceToStr
                }));

                const dialog = new Dialog(this, {
                    size: 'medium',
                    title: "Calcula tus cuotas",
                    renderFooter: false ,
                    $content: content ,
                });
                dialog._opened.then(() => {
                    let card_selector = dialog.el.querySelector('.o_card_selector');
                    card_selector.addEventListener('change', function(event){
                        self._onChangeDialogCardSelector(event, dialog.el);
                    });
                });
                dialog.open();

            });
        },
        _onChangeDialogCardSelector : function(event, dialog_element){
            let selected_card = event.target.options[event.target.selectedIndex];
            let all_installment_list = dialog_element.querySelectorAll('.o_card_list');
            for(var i = 0, all = all_installment_list.length; i < all; i++){
                all_installment_list[i].classList.add("d-none");
            }
            if (selected_card.value){
                let installment_list = dialog_element.querySelector('#o_card_' + selected_card.value);
                if (installment_list) installment_list.classList.remove("d-none");
            }

        },
        _onChangeCardSelector : function(event){
            let selected_card = event.target.options[event.target.selectedIndex];
            let all_installment_list = this.el.querySelectorAll('.o_card_list');
            for(var i = 0, all = all_installment_list.length; i < all; i++){
                all_installment_list[i].classList.add("d-none");
            }
            if (selected_card.value){
                let installment_list = this.el.querySelector('#o_card_' + selected_card.value);
                installment_list.classList.remove("d-none");
            }

        },
    });
});
