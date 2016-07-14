# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
import openerp
from openerp import http
from openerp.http import request
import openerp.addons.website_sale.controllers.main


class website_sale(openerp.addons.website_sale.controllers.main.website_sale):

    @http.route(['/shop/payment2'], type='http', auth="public", website=True)
    def payment2(self, **post):
    # def payment(self, **post):
        print 'aaaaaaaaaaaaaaaaaaaa'
        print 'bbbbbbbbbbbbb'
        print 'bbbbbbbbbbbbb'
        print 'bbbbbbbbbbbbb'
        print 'aaaaaaaaaaaaaaaaaaaa'
        cr, uid, context = request.cr, request.uid, request.context
        order = request.website.sale_get_order(context=context)
        internal_note = post.get('internal_note')
        print 'order', order
        print 'aaaaaaaaaaaaaaaaaaaa internal_note', internal_note
        # print 'aaaaaaaaaaaaaaaaaaaa carrier_id', carrier_id
        # if observation:
            # carrier_id = int(carrier_id)
        if order and internal_note:
            request.registry['sale.order'].write(
                cr, uid, order.id, {'internal_notes': internal_note},
                context=context)
            # request.registry['sale.order']._check_carrier_quotation(cr, uid, order, force_carrier_id=carrier_id, context=context)
            # if carrier_id:
                # return request.redirect("/shop/payment")

        # res = super(website_sale, self).payment(**post)
        # raise Warning('asd')
        # return res

# class TodoPagoController(http.Controller):

#     @http.route([
#         '/payment/todopago/create_preference',
#     ],
#         type='http', auth="none")
#     def todopago_create_preference(self, **post):
#         _logger.info(
#             'todopago: create preference with post data %s',
#             pprint.pformat(post))
#         # TODO podriamos pasar cada elemento por separado para no necesitar
#         # el literal eval
#         todopago_data = literal_eval(post.get('todopago_data', {}))
#         if not todopago_data:
#             return werkzeug.utils.redirect("/")
#         acquirer_id = todopago_data.get('acquirer_id')
#         cr, uid, context = request.cr, SUPERUSER_ID, request.context
#         request_url = request.registry[
#             'payment.acquirer']._todopago_create_transaction(
#             cr, uid, acquirer_id, post, context)
#         return werkzeug.utils.redirect(request_url)

#     def todopago_validate(self, **post):
#         "Validate mercado pago payment from a return URL or IPN"
#         _logger.info(
#             'Validating todopago payment with post data %s',
#             pprint.pformat(post))
#         cr, uid, context = request.cr, SUPERUSER_ID, request.context
#         request.registry['payment.transaction'].form_feedback(
#             cr, uid, post, 'todopago', context)
#         return False
