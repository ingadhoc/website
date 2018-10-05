from odoo import models, api


class ResPartner(models.Model):

    _inherit = 'res.partner'

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
