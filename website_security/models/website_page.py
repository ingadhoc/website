##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import api, fields, models


class Page(models.Model):
    _inherit = "website.page"

    groups_id = fields.Many2many(
      'res.groups',
      string='Groups'
    )

    @api.one
    def _compute_visible(self):
        self.is_visible = self.website_published and (
            not self.date_publish or self.date_publish < fields.Datetime.now()) and (
                not self.groups_id or self.env.user.groups_id & self.groups_id)