odoo.define('website_sale_note.internal_notes', function (require) {
"use strict";

    require('website.website');
    var ajax = require('web.ajax');

    $(document).ready(function () {
        $('.oe_sale_acquirer_button').on('click',function(ev) {
            var internal_notes = $('#internal_notes').val();
            ajax.jsonRpc('/shop/payment/add_note', 'call',
                {'internal_notes': internal_notes}).then(function (res) {
            }).fail(function (err) {
                console.log(err);
            });
        });
    });

});
