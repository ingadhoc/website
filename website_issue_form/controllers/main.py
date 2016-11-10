# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
import base64

import werkzeug
import werkzeug.urls

from openerp import http, SUPERUSER_ID
from openerp.http import request
from openerp.tools.translate import _


class contactus(http.Controller):

    def generate_google_map_url(self, street, city,
                                city_zip, country_name):
        url = "http://maps.googleapis.com/maps/api/staticmap?" \
              "center=%s&sensor=false&zoom=8&size=298x298" % \
              werkzeug.url_quote_plus(
                  '%s, %s %s, %s' % (street, city,
                                     city_zip, country_name))
        return url

    @http.route(['/page/website.issue', '/page/issue'],
                type='http', auth="public", website=True)
    def contact(self, **kwargs):
        values = {}
        for field in ['description', 'partner_name',
                      'phone', 'contact_name',
                      'email_from', 'name']:
            if kwargs.get(field):
                values[field] = kwargs.pop(field)
        values.update(kwargs=kwargs.items())
        return request.website.render("website.issue", values)

    def create_issue(self, request, values, kwargs):
        """ Allow to be overrided """
        return request.registry['project.issue'].create(
            request.cr, SUPERUSER_ID, values, request.context)

    def preRenderThanks(self, request, values, kwargs):
        """ Allow to be overrided """
        company = request.website.company_id
        return {
            'google_map_url': self.generate_google_map_url(
                company.street, company.city, company.zip,
                company.country_id and
                company.country_id.name_get()[0][1] or ''),
            '_values': values,
            '_kwargs': kwargs,
        }

    @http.route(['/project/issue'], type='http',
                auth="public", website=True)
    def contactus(self, **kwargs):
        # print 'aaaaaaaa'

        def dict_to_str(title, dictvar):
            ret = "\n\n%s" % title
            for field in dictvar:
                ret += "\n%s" % field
            return ret

        # Only use for behavior, don't stock it
        _TECHNICAL = ['show_info', 'view_from', 'view_callback']
        _BLACKLIST = ['id', 'create_uid', 'create_date', 'write_uid',
                      'write_date', 'user_id', 'active']
        # Allow in description
        # Could be improved including required from model
        _REQUIRED = ['name', 'email_from', 'description']
        # TODO: esto no funciono, hay que mejorarlo
        # _REQUIRED = ['name', 'contact_name', 'email_from', 'description']

        # List of file to add to ir_attachment once we have the ID
        post_file = []
        post_description = []  # Info to add after the message
        values = {}

        for field_name, field_value in kwargs.items():
            if hasattr(field_value, 'filename'):
                post_file.append(field_value)
            elif field_name in request.registry[
                'project.issue']._all_columns\
                    and field_name not in _BLACKLIST:
                values[field_name] = field_value
            # allow to add some free fields or blacklisted field like ID
            elif field_name not in _TECHNICAL:
                post_description.append("%s: %s" % (field_name, field_value))

        # if kwarg.name is empty, it's an error, we cannot copy the
        # contact_name
        if "name" not in kwargs and values.get("contact_name"):
            values["name"] = values.get("contact_name")
        # fields validation : Check that required field from model crm_lead
        # exists
        error = set(field for field in _REQUIRED if not values.get(field))
        values = dict(values, error=error)
        # Omitimos esto porque nos daba error
        # if error:
        #     values.update(kwargs=kwargs.items())
        # return request.website.render(kwargs.get("view_from",
        # "website.issue"), values)

        try:
            domains = [
                [('name', '=', kwargs.get("contact_name"))],
                [('email', '=', kwargs.get("email_from"))],
                [('name', '=', kwargs.get("partner_name"))],
            ]
            for domain in domains:
                partner_ids = request.registry['res.partner'].search(
                    request.cr, SUPERUSER_ID, domain)
                if partner_ids:
                    values['partner_id'] = partner_ids[0]
                    continue
        except ValueError:
            pass

        # description is required, so it is always already initialized
        if post_description:
            values[
                'description'] += \
                dict_to_str(_("Custom Fields: "), post_description)

        if kwargs.get("show_info"):
            post_description = []
            environ = request.httprequest.headers.environ
            post_description.append(
                "%s: %s" % ("IP", environ.get("REMOTE_ADDR")))
            post_description.append(
                "%s: %s" % ("USER_AGENT", environ.get("HTTP_USER_AGENT")))
            post_description.append(
                "%s: %s" % ("ACCEPT_LANGUAGE",
                            environ.get("HTTP_ACCEPT_LANGUAGE")))
            post_description.append(
                "%s: %s" % ("REFERER", environ.get("HTTP_REFERER")))
            values[
                'description'] += \
                dict_to_str(_("Environ Fields: "), post_description)
        issue_id = self.create_issue(
            request, dict(values, user_id=False), kwargs)
        if issue_id:
            for field_value in post_file:
                attachment_value = {
                    'name': field_value.filename,
                    'res_name': field_value.filename,
                    'res_model': 'crm.lead',
                    'res_id': issue_id,
                    'datas': base64.encodestring(field_value.read()),
                    'datas_fname': field_value.filename,
                }
                request.registry['ir.attachment'].create(
                    request.cr, SUPERUSER_ID,
                    attachment_value, context=request.context)

        values = self.preRenderThanks(request, values, kwargs)
        return request.website.render(
            kwargs.get("view_callback",
                       "website_issue_form.issue_thanks"), values)
