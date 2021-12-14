from odoo import models


class Website(models.Model):

    _inherit = 'website'

    def _get_warehouse_available(self):
        res = super()._get_warehouse_available()
        if res:
            res = self.env['stock.warehouse'].search([('website_published', '=', True), ('id', '=', res)]).id
        return res
