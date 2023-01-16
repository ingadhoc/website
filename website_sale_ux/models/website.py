from odoo import fields, models
from odoo.http import request
from odoo.exceptions import UserError

from datetime import datetime, timedelta

class Website(models.Model):
    _inherit = 'website'

    def _prepare_sale_order_values(self, partner, pricelist):

        values = super()._prepare_sale_order_values(partner, pricelist)
        ban_duration = int(self.env['ir.config_parameter'].sudo().get_param('website.order_banned_minutes', '30'))

        values['ip_address'] = request.httprequest.environ['REMOTE_ADDR']
        from_time =datetime.now() - timedelta(minutes=ban_duration)
        block_count = self.env['website.block_ip'].sudo().search_count([
            ('name', '=', values['ip_address']),
            ('create_date', '>', from_time),
        ])

        if block_count > 0:
            raise UserError('Your Order blocked')


        ban_duration = int(self.env['ir.config_parameter'].sudo().get_param('website.order_banned_after', '3'))

        from_time = datetime.now() - timedelta(seconds=60)
        order_count = self.env['sale.order'].sudo().search_count([
            ('ip_address', '=', values['ip_address']),
            ('create_date', '>', from_time),
        ])
        if order_count >= 3:
            self.env['website.block_ip'].sudo().create({'name': values['ip_address']})
            self._cr.commit()
            raise UserError('Demasiadas ordenes creadas')

        return values


class WebsiteBlockIP(models.Model):

    _name = 'website.block_ip'
    _description = 'blocked ips'

    name = fields.Char('Ip', index=True)
