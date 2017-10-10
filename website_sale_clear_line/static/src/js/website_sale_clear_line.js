odoo.define('website_sale.clear_cart_line', function (require) {
"use strict";
    require('website.website');
    var ajax = require('web.ajax');

$(document).ready(function () {
    var oe_website_sale = this;
    $(oe_website_sale).on("click", ".oe_cart #clear_cart_line_button", function () {
        // obtenemos la linea de la vista
        var $input = $(this);
        var line_id = parseInt($input.data('line-id'),10);
        // pasamos la linea del pedido
        ajax.jsonRpc("/shop/clear_cart_line", "call", {
                'line_id': line_id
            }).then(function(){
            location.reload();
        })
        return false;
    })
})
});