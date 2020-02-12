##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import fields, models


class Page(models.Model):
    _inherit = "website.page"

    groups_id = fields.Many2many(
        'res.groups',
        string='Groups',
        help='Si elige algun grupo, solo sera visible para usuarios de ese '
        'grupo',
    )

    def _compute_visible(self):
        user = self.env['res.users'].browse(self._context.get('uid', False)) or self.env.user
        for rec in self:
            rec.is_visible = rec.website_published and (
                not rec.date_publish
                or rec.date_publish < fields.Datetime.now()) and (
                not rec.groups_id
                or user.groups_id & rec.groups_id)
