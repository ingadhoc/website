##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo.addons.website_sale_delivery.controllers.main \
    import WebsiteSaleDelivery
from odoo.http import request, route


class L10nArWebsiteSale(WebsiteSaleDelivery):

    @route()
    def update_eshop_carrier(self, **post):
        res = super(L10nArWebsiteSale, self).update_eshop_carrier(**post)
        order = request.website.sale_get_order()
        currency = order.currency_id
        res.update({
            'new_amount_delivery': self._format_amount(
                order.report_amount_delivery, currency),
        })
        return res

    def order_2_return_dict(self, order):
        """ Returns the tracking_cart dict of the order for Google analytics
        """
        res = super(L10nArWebsiteSale, self).order_2_return_dict(order)
        for line in order.order_line:
            if line.is_delivery:
                res['transaction']['shipping'] = line.report_price_unit
        return res
