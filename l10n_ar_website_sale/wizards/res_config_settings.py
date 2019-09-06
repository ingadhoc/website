from odoo import fields, models, api


class ResConfigSettings(models.TransientModel):

    _inherit = 'res.config.settings'

    sale_use_taxes_default = fields.Selection(
        [('b2c', 'Consumidor Final (B2C)'),
         ('b2b', 'Empresa (B2B)')],
        default='b2c',
        required=True,
        help="* Consumidor Final: Impuesto incluido en precio (B2C)\n"
        "* Empresa: Impuestos detallados por separado (B2B)",
        string="Tipo de venta al publico",
    )

    @api.model
    def get_values(self):
        res = super().get_values()
        res.update({'sale_use_taxes_default': self.env[
            'ir.config_parameter'].sudo().get_param(
                'l10n_ar_website_sale.sale_use_taxes_default', 'b2c'),
        })
        return res

    @api.multi
    def set_values(self):
        super().set_values()
        self.env['ir.config_parameter'].sudo().set_param(
            'l10n_ar_website_sale.sale_use_taxes_default',
            self.sale_use_taxes_default
        )
