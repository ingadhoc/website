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
        if all_values.get('commercial_partner_id', False):
            commercial_fields = [
                'main_id_number', 'main_id_category_id',
                'afip_responsability_type_id']
            for item in commercial_fields:
                checkout.pop(item, False)
                all_values.pop(item, False)
        res = super(L10nArWebsiteSale, self)._checkout_form_save(
            mode=mode, checkout=checkout, all_values=all_values)
        return res

    def checkout_form_validate(self, mode, all_form_values, data):
        error, error_message = super(
            L10nArWebsiteSale, self).checkout_form_validate(
                mode=mode, all_form_values=all_form_values, data=data)
        write_error, write_message = \
            request.env['res.partner'].sudo().try_write_commercial(
                all_form_values)
        if write_error:
            error.update(write_error)
            error_message.extend(write_message)
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

    @route()
    def shop(self, page=0, category=None, search='', ppg=False, **post):
        response = super(L10nArWebsiteSale, self).shop(
            page=page, category=category, search=search, ppg=ppg, **post)
        vat_discriminated = request.env['res.partner']._get_vat_discriminated(
            request.env.user.partner_id,
            request.env.user.company_id)
        response.qcontext.update({'vat_discriminated': vat_discriminated})
        return response
