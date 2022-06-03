from odoo import models


class Website(models.Model):

    _inherit = 'website'

    def _get_warehouse_available(self):
        # import pdb; pdb.set_trace()
        # this method is called to get stock and it's overriding by this module on _get_domain_locations so that
        # it get stock for all published wareouse, but it's also used to set warehouse on SO
        # for this second use case we only return the warehouse if it's published
        res = super()._get_warehouse_available()
        if res:
            res = self.env['stock.warehouse'].sudo().search(
                [('website_published', '=', True), ('id', '=', res)], limit=1).id
        return res
