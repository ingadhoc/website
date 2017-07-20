# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp.http import request
from openerp import tools
from openerp.tools.translate import _
from openerp.addons.website_sale.controllers.main import website_sale
from openerp.addons.website_portal.controllers.main import WebsiteAccount


class WebsiteSale(website_sale):

    def _get_mandatory_billing_fields(self):
        res = super(WebsiteSale, self)._get_mandatory_billing_fields()
        if 'street2' in res:
            res.remove('street2')
        if 'street' not in res:
            res.append('street')
        return self.mandatory_billing_fields

    def _get_optional_billing_fields(self):
        res = super(WebsiteSale, self)._get_optional_billing_fields()
        if 'street' in res:
            res.remove('street')
        if 'street2' not in res:
            res.append('street2')
        return self.optional_billing_fields


class WebsiteAccount(WebsiteAccount):

    def details_form_validate(self, data):
        error = dict()
        error_message = []

        mandatory_billing_fields = [
            'name', 'phone', 'email', 'street', 'city', 'country_id'
        ]

        # Validation
        for field_name in mandatory_billing_fields:
            if not data.get(field_name):
                error[field_name] = 'missing'

        # email validation
        if not tools.single_email_re.match(data.get('email', '')):
            error['email'] = 'error'
            error_message.append(
                _('Invalid Email! Please enter a valid email address.'))

        # vat validation
        if (data.get('vat') and
                hasattr(request.env['res.partner'], 'check_vat')):
            if request.website.company_id.vat_check_vies:
                # force full VIES online check
                check_func = request.env['res.partner'].vies_vat_check
            else:
                # quick and partial off-line checksum validation
                check_func = request.env['res.partner'].simple_vat_check
            vat_country, vat_number = request.env['res.partner']._split_vat(
                data.get('vat'))
            if not check_func(vat_country, vat_number):  # simple_vat_check
                error['vat'] = 'error'
        # error message for empty required fields
        if [err for err in error.values() if err == 'missing']:
            error_message.append(_('Some required fields are empty.'))

        return error, error_message
