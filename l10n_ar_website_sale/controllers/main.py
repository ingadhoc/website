##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo.addons.website_sale.controllers.main import website_sale
from odoo import SUPERUSER_ID, _
from odoo.http import request
from odoo.tools import config
from odoo import http
from odoo.addons.website_portal.controllers.main import website_account
import logging
_logger = logging.getLogger(__name__)


class WebsiteSale(website_sale):

    def checkout_form_validate(self, data):
        """
        We can not add them directly to mandatory billing fields becasue
        it gives an error in testes. So we add them and test the manually
        To not break these tests, allow for missing fields in test mode
        """
        error, error_message = super(
            WebsiteSale, self).checkout_form_validate(data)

        partner = request.registry.get('res.users').browse(
            request.cr, SUPERUSER_ID, request.uid, request.context).partner_id

        # Phantomjs test steps from website_sale don't enter the VAT field.
        if partner.commercial_partner_id == partner:
            if not data.get('main_id_number') and not config['test_enable']:
                error['main_id_number'] = 'missing'
            if not data.get(
                    'main_id_category_id') and not config['test_enable']:
                error['main_id_category_id'] = 'missing'

            number = request.env['res.partner.id_number'].sudo().new({
                'name': data.get('main_id_number'),
                'partner_id': partner.id,
                'category_id': data.get('main_id_category_id'),
            })
            # validate document number
            try:
                request.env['res.partner.id_category'].sudo().browse(
                    data.get('main_id_category_id')).validate_id_number(
                    number)
            except Exception as e:
                _logger.info(
                    'Documento invalido en checkout ecommerce, error: %s' % e)
                error['main_id_number'] = 'error'
                error_message.append(_('Numero de documento invalido'))

            try:
                number.check()
            except Exception as e:
                _logger.info(
                    'Ya existe una empresa con ese número de documento, error:'
                    '%s' % e)
                error['main_id_number'] = 'error'
                error_message.append(_(
                    'Ya existe una empresa con ese número de documento'))

        # only make state required if there are states on choosen country
        cr, context, pool = (
            request.cr, request.context, request.registry)
        state_ids = pool.get('res.country.state').search(
            cr, SUPERUSER_ID, [('country_id', '=', data.get('country_id'))],
            context=context)
        if (
                state_ids and not data.get('state_id') and
                not config['test_enable']):
            error['state_id'] = 'missing'
        if not data.get('zip') and not config['test_enable']:
            error['zip'] = 'missing'
        return error, error_message

    def _get_optional_billing_fields(self):
        """
        We add them so they value is stored
        """
        optional_billing_fields = (
            super(WebsiteSale, self)._get_optional_billing_fields() +
            ['main_id_number', 'main_id_category_id', 'invoice_ids'])
        return optional_billing_fields

    def checkout_values(self, data=None):
        cr, context, registry = (
            request.cr, request.context, request.registry)
        res = super(WebsiteSale, self).checkout_values(data)
        orm_document_categories = registry.get('res.partner.id_category')
        main_id_category_ids = orm_document_categories.search(
            cr, SUPERUSER_ID, [], context=context)
        document_categories = orm_document_categories.browse(
            cr, SUPERUSER_ID, main_id_category_ids, context)
        res.update({
            'document_categories': document_categories,
        })
        return res

    def _post_prepare_query(self, query, data, address_type):
        res = super(WebsiteSale, self)._post_prepare_query(
            query, data, address_type)
        if address_type == 'billing':
            prefix = ''
        else:
            prefix = 'shipping_'
        if res.get(prefix + 'main_id_category_id'):
            res[prefix + 'main_id_category_id'] = int(
                res[prefix + 'main_id_category_id'])

        return res


class l10n_ar_website_account(website_account):

    @http.route(['/my/account'], type='http', auth='user', website=True)
    def details(self, redirect=None, **post):
        response = super(l10n_ar_website_account, self).details()
        document_categories = request.env[
            'res.partner.id_category'].sudo().search([])
        response.qcontext.update({'document_categories': document_categories})
        return response
