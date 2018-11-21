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
        post_process = False
        commercial_partner_id = all_values.get('commercial_partner_id', False)
        if commercial_partner_id:
            post_process = True
            commercial_fields = [
                'main_id_number',
                'main_id_category_id',
                'afip_responsability_type_id',
            ]
            values = {}
            for item in commercial_fields:
                values.update({
                    item: checkout.pop(item, all_values.pop(item))
                })

        res = super(L10nArWebsiteSale, self)._checkout_form_save(
            mode=mode, checkout=checkout, all_values=all_values)

        if post_process:
            commercial_partner = request.env['res.partner'].browse(
                int(commercial_partner_id))
            values = self.remove_readonly_required_fields(
                commercial_partner, commercial_fields, values)
            if values:
                commercial_partner.sudo().write(values)
        return res

    def remove_readonly_required_fields(
        self, record, required_fields, values):
        """ In some cases we have information showed to the user in the form
        that is required but that is already set and reaadonly.
        We do not really update this fields and then here we are trying to
        write them: the problem is that this fields has a constraint if
        we are trying to re-write them (even when is the same value).

        This method remove this (field, values) for the values to write in
        order to do avoid the constraint and not re-writed again when they
        has been already writed.

        param: @record (recordset) the recorset to compore
        param: @required_fields: (list) fields of the fields that we want to
               check
        param: @values (dict) the values of the web form

        return: the same values to write and they do not include
        required/readonly fields.
        """
        for r_field in required_fields:
            value = values.get(r_field)
            if r_field.endswith('_id'):
                if str(record[r_field].id) == value:
                    values.pop(r_field, False)
            else:
                if record[r_field] == value:
                    values.pop(r_field, False)
        return values

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
