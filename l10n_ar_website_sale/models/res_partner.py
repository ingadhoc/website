from odoo import models, api


class ResPartner(models.Model):

    _inherit = 'res.partner'

    def get_company_partner(self):
        # Get company
        website_id = self._context.get('website_id', False)
        if website_id:
            company_id = self.env['website'].browse(website_id).company_id.id
        else:
            company_id = self._context.get(
                'company_id', self.env.user.company_id.id)
        company = self.env['res.company'].browse(company_id)

        # Get parter
        user_id = self._context.get('uid', self.env.user.id)
        partner = self.env['res.users'].browse(user_id).partner_id
        return company, partner

    @api.model
    def _get_vat_discriminated(self, partner, company):
        vat_discriminated = True
        company_vat_type = company.sale_allow_vat_no_discrimination
        if company_vat_type and company_vat_type != 'discriminate_default':
            letters = self.env['account.journal']._get_journal_letter(
                'sale', company,
                partner.commercial_partner_id)
            if letters:
                vat_discriminated = not letters[0].taxes_included
            # if no responsability or no letters
            if not letters and \
                    company_vat_type == 'no_discriminate_default':
                vat_discriminated = False
        return vat_discriminated
