from odoo import models, fields


class ProductTemplate(models.Model):

    _inherit = 'product.template'

    vat_tax_id = fields.Many2one(
        'account.tax',
        compute='_compute_vat_tax_id',
    )

    def _compute_vat_tax_id(self):
        current_website = self.env['website'].get_current_website()
        company_id = current_website.company_id
        for rec in self:
            vat_taxes = rec.taxes_id.filtered(lambda x: (
                x.tax_group_id.type == 'tax' and
                x.tax_group_id.tax == 'vat' and x.company_id == company_id))
            rec.vat_tax_id = vat_taxes and vat_taxes[0].id
