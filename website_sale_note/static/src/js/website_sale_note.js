$(document).ready(function() { 
    $('.oe_sale_acquirer_button').on('click',function(ev) {
        var internal_notes = $('#internal_notes').val();
        openerp.jsonRpc('/shop/payment/add_note', 'call',
            {'internal_notes': internal_notes}).then(function (res) {
        }).fail(function (err) {
            console.log(err);
        });
    });
});