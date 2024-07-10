from odoo import api, fields, models, _
from ast import literal_eval
from odoo.exceptions import AccessError, UserError

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    website_extend_search_fields = fields.Boolean(
        string="Extend website search fields",
        readonly=False,
        config_parameter='website_sale_search_improved.extend_search_fields'
    )
    website_search_fields_list = fields.Char(
        default='[]',
        config_parameter='website_sale_search_improved.search_fields'
    )

    @api.constrains('website_search_fields_list')
    def _check_website_search_fields_list(self):

        try:
            extra_search_fields = literal_eval(self.website_search_fields_list)
        except ValueError:
            raise UserError("The field should be a list of fields")

        if not all(isinstance(element, str) for element in extra_search_fields):
            raise UserError("The field should be a list of fields")

        for field_path in extra_search_fields:
            self.check_field_path(field_path.split('.'), 'product.template')

    def check_field_path(self, fields_list, model):
        """ recursive method to check if:
             - the field path exists
             - the public user has access to all the models in the field path
        """
        main_field = fields_list[0]
        field = self.env[model]._fields.get(main_field)
        if not field:
            raise UserError("The field %s is not in the model %s" % (main_field, model))
        self.check_model_public_access(field.model_name)

        if not field.relational and fields_list[1:]:
            raise UserError("The field %s is not a relational field" % main_field)

        if field.relational:
            if fields_list[1:]:
                return self.check_field_path(fields_list[1:], field.comodel_name)
            else:
                raise UserError(
                    "The field %s is relational so you must specify in which field of the model %s search (e.g. '%s.name')"
                    "" % (main_field, field.comodel_name, main_field))

    def check_model_public_access(self, model):
        public_user = self.env.ref('base.public_user', raise_if_not_found=False)
        try:
            self.with_user(public_user).env[model].check_access_rights('read')
        except AccessError:
            raise UserError(_("The public user do not have access to the model %s" % (model)))

