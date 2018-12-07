##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.http import request, route
from odoo.tools import config


class L10nArWebsiteSale(WebsiteSale):

    def _get_mandatory_billing_fields(self):
        # para no romper los test de odoo
        res = super(L10nArWebsiteSale, self)._get_mandatory_billing_fields()
        if not config['test_enable']:
            res += ["zip"]
        return res + [
            "main_id_category_id", "main_id_number",
            "afip_responsability_type_id",
        ]

    def _checkout_form_save(self, mode, checkout, all_values):
        # Extract data from commercial partner
        post_process = False
        commercial_partner, commercial_fields, values = \
            request.env['res.partner'].sudo().get_commercial_data(
                all_values)
        if commercial_partner:
            post_process = True
            for item in commercial_fields:
                checkout.pop(item, False)
                all_values.pop(item, False)

        res = super(L10nArWebsiteSale, self)._checkout_form_save(
            mode=mode, checkout=checkout, all_values=all_values)

        # Write data on commercial partner
        if post_process:
            if commercial_partner and values:
                commercial_partner.sudo().write(values)
        return res

    def checkout_form_validate(self, mode, all_form_values, data):
        error, error_message = super(
            L10nArWebsiteSale, self).checkout_form_validate(
                mode=mode, all_form_values=all_form_values, data=data)

        # Validate commercial partner
        main_id_number = data.get('main_id_number', all_form_values)
        main_id_category_id = data.get('main_id_category_id', all_form_values)
        if main_id_number and main_id_category_id:
            commercial_partner, _commercial_fields, values = \
                request.env['res.partner'].sudo().get_commercial_data(
                    all_form_values, data)
            exc_error, exc_message = \
                commercial_partner.sudo().catch_number_id_exceptions(values)
            if exc_error:
                error.update(exc_error)
                error_message.extend(exc_message)
        return error, error_message

    @route()
    def address(self, **kw):
        response = super(L10nArWebsiteSale, self).address(**kw)
        document_categories = request.env[
            'res.partner.id_category'].sudo().search([])
        afip_responsabilities = request.env[
            'afip.responsability.type'].sudo().search([])
        uid = request.session.uid or request.env.ref('base.public_user').id
        Partner = request.env['res.users'].browse(uid).partner_id
        Partner = Partner.with_context(show_address=1).sudo()
        response.qcontext.update({
            'document_categories': document_categories,
            'afip_responsabilities': afip_responsabilities,
            'partner': Partner,
        })
        return response

    # TODO review: Aca podria ser necesario pasar el afip_responsabilities
    @route()
    def checkout(self, **post):
        super(L10nArWebsiteSale, self).checkout(**post)
        # _response = super(L10nArWebsiteSale, self).checkout(**post)
        order = request.website.sale_get_order()
        redirection = self.checkout_redirection(order)
        if redirection:
            return redirection

        if order.partner_id.id == request.website.user_id.sudo().partner_id.id:
            return request.redirect('/shop/address')

        # --------------------------------------------------------------------
        # Odoo original code
        # for f in self._get_mandatory_billing_fields():
        #     if not order.partner_id[f]:
        #         return request.redirect('/shop/address?partner_id=%d' %
        #             order.partner_id.id)
        # Our code
        mandatory_billing_fields = self._get_mandatory_billing_fields()
        commercial_billing_fields = ["main_id_category_id", "main_id_number",
                                     "afip_responsability_type_id"]
        for item in commercial_billing_fields:
            mandatory_billing_fields.pop(mandatory_billing_fields.index(item))

        for f in mandatory_billing_fields:
            if not order.partner_id[f]:
                return request.redirect(
                    '/shop/address?partner_id=%d' % order.partner_id.id)
        for f in commercial_billing_fields:
            if not order.partner_id.commercial_partner_id[f]:
                return request.redirect(
                    '/shop/address?partner_id=%d' % order.partner_id.id)
        # end
        # --------------------------------------------------------------------

        values = self.checkout_values(**post)

        values.update({'website_sale_order': order})

        # Avoid useless rendering if called in ajax
        if post.get('xhr'):
            return 'ok'
        return request.render("website_sale.checkout", values)

    @route()
    def product(self, product, category='', search='', **kwargs):
        response = super(L10nArWebsiteSale, self).product(
            product=product, category=category, search=search, **kwargs)
        vat_discriminated = request.env['res.partner']._get_vat_discriminated(
            request.env.user.partner_id,
            request.env.user.company_id)
        response.qcontext.update({'vat_discriminated': vat_discriminated})
        return response
