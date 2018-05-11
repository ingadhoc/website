##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import api, fields, models


class WebsiteMenu(models.Model):
    _inherit = "website.menu"

    related_view_id = fields.Many2one(
        related='page_id.view_id',
        readonly=True
    )

    group_ids = fields.Many2many(
        'res.groups',
        'website_menu_group_rel',
        'menu_id',
        'gid',
        'Groups',
        # domain=[('is_portal', '=', True)],
        context={'default_is_portal': True},
        help="If you have groups, the visibility of this menu will be based "
        "on these groups. "
        "If this field is empty, Odoo will compute visibility based on the "
        "related object's read access."
    )

    @api.multi
    @api.onchange('group_ids')
    def change_groups(self):
        for rec in self:
            if rec.related_view_id and not rec.related_view_id.groups_id:
                rec.related_view_id.write(
                    {'groups_id': [(6, False, rec.group_ids.ids)]})

    @api.multi
    def write(self, vals):
        res = super(WebsiteMenu, self).write(vals)
        self.add_rights_submenu()
        return res

    def add_rights_submenu(self):
        if self.parent_id and self.parent_id.group_ids and not self.group_ids:
            self.group_ids = self.parent_id.group_ids.ids
        if self.related_view_id and not self.related_view_id.groups_id:
            self.related_view_id.write(
                {'groups_id': [(6, False, self.group_ids.ids)]})
