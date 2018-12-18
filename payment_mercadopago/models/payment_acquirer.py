##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
import urllib.parse as urlparse
from odoo.addons.payment.models.payment_acquirer import ValidationError
from ..controllers.main import MercadoPagoController
from odoo import api, fields, models, _
import werkzeug


class AcquirerMercadopago(models.Model):
    _inherit = 'payment.acquirer'

    provider = fields.Selection(
        selection_add=[('mercadopago', 'MercadoPago')],
    )
    mercadopago_item_title = fields.Char(
        'MercadoPago Item Title',
        help='Yo need to use %s to indicate '
             'where SO number must go',
        default='Orden Ecommerce %s',
    )
    mercadopago_client_id = fields.Char(
        'MercadoPago Client Id',
        required_if_provider='mercadopago',
    )
    mercadopago_secret_key = fields.Char(
        'MercadoPago Secret Key',
        required_if_provider='mercadopago',
    )

    def _get_feature_support(self):
        res = super(AcquirerMercadopago, self)._get_feature_support()
        res['fees'].append('mercadopago')
        return res

    @api.multi
    def mercadopago_compute_fees(self, amount, currency_id, country_id):
        self.ensure_one()
        if not self.fees_active:
            return 0.0
        country = self.env['res.country'].browse(country_id)
        if country and self.company_id.country_id.id == country.id:
            percentage = self.fees_dom_var
            fixed = self.fees_dom_fixed
        else:
            percentage = self.fees_int_var
            fixed = self.fees_int_fixed
        fees = percentage / 100.0 * amount + fixed
        return fees

    @api.multi
    def mercadopago_form_generate_values(self, values):
        self.ensure_one()
        tx_values = dict(values)
        base_url = self.env['ir.config_parameter'].sudo().get_param(
            'web.base.url')
        if (
                not self.mercadopago_client_id or
                not self.mercadopago_secret_key):
            raise ValidationError(_(
                'YOU MUST COMPLETE acquirer.mercadopago_client_id and '
                'acquirer.mercadopago_secret_key'))

        success_url = MercadoPagoController._success_url
        failure_url = MercadoPagoController._failure_url
        pending_url = MercadoPagoController._pending_url
        return_url = tx_values.get('return_url')
        # si hay return_url se la pasamos codificada asi cuando vuelve
        # nos devuelve la misma
        if return_url:
            url_suffix = '{}{}'.format(
                '?', werkzeug.urls.url_encode({'return_url': return_url}))
            success_url += url_suffix
            failure_url += url_suffix
            pending_url += url_suffix

        # TODO, implement, not implemented yet because mercadopago only
        # shows description of first line and we would need to send taxes too
        # sale_order = self.env['sale.order'].search(
        #     [('name', '=', tx_values["reference"])], limit=1)
        # if self.mercadopago_description == 'so_lines' and sale_order:
        #     items = [{
        #         "title": line.name,
        #         "quantity": line.product_uom_qty,
        #         "currency_id": (
        #             tx_values['currency'] and
        #             tx_values['currency'].name or ''),
        #         "unit_price": line.price_unit,
        #     } for line in sale_order.order_line]
        # else:
        if (
                not self.mercadopago_item_title or
                "%s" not in self.mercadopago_item_title):
            raise ValidationError(_(
                'No generic message defined for mercadopago or message '
                'does not contains %/s!'))
        items = [{
            "title": self.mercadopago_item_title % (
                tx_values["reference"]),
            "quantity": 1,
            "currency_id": (
                tx_values['currency'] and
                tx_values['currency'].name or ''),
            "unit_price": tx_values["amount"],
        }]

        if self.fees_active:
            items.append({
                "title": _('Recargo por Mercadopago'),
                "quantity": 1,
                "currency_id": (
                    tx_values['currency'] and
                    tx_values['currency'].name or ''),
                "unit_price": tx_values.pop('fees', 0.0),
            })

        preference = {
            "items": items,
            "payer": {
                "name": values["billing_partner_first_name"],
                "surname": values["billing_partner_last_name"],
                "email": values["partner_email"],
            },
            "back_urls": {
                "success": '%s' % urlparse.urljoin(
                    base_url, success_url),
                "failure": '%s' % urlparse.urljoin(
                    base_url, failure_url),
                "pending": '%s' % urlparse.urljoin(
                    base_url, pending_url)
            },
            "auto_return": "approved",
            "external_reference": tx_values["reference"],
            "expires": False,
        }
        tx_values.update({
            'mercadopago_data': {
                'mercadopago_preference': preference,
                'mercadopago_client_id': self.mercadopago_client_id,
                'mercadopago_secret_key': self.mercadopago_secret_key,
                'environment': self.environment,
            }})
        return tx_values

    @api.multi
    def mercadopago_get_form_action_url(self):
        self.ensure_one()
        return MercadoPagoController._create_preference_url
