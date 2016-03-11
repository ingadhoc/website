$(document).ready(function () {
$('.oe_website_sale').each(function () {
    var oe_website_sale = this;
    $(oe_website_sale).on("click", ".oe_cart #clear_cart_line_button", function () {
        // obtenemos la linea de la vista
        var $input = $(this);
        var line_id = parseInt($input.data('line-id'),10);
        // pasamos la linea del pedido
        openerp.jsonRpc("/shop/clear_cart_line", "call", {
                'line_id': line_id
            }).then(function(){
            location.reload();
        })
        return false;
    })

})
})