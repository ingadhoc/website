from odoo import models


class Website(models.Model):

    _inherit = 'website'

    def _get_warehouse_available(self):
        """this method is called to get stock and it's overriding by this module on _get_domain_locations so that
        it get stock for all published wareouse, but it's also used to set warehouse on SO
        for this second use case we only return the warehouse if it's published"""
        self.ensure_one()
        res = super()._get_warehouse_available()

        if res and self.env['stock.warehouse'].sudo().browse(res).website_published:
            return res
        return self.env['stock.warehouse'].sudo().search(
            [('website_published', '=', True), ('company_id', '=', self.company_id.id)], limit=1).id
