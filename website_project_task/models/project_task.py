# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################

from openerp import api, models


class ProjectTask(models.Model):
    _name = "project.task"
    _inherit = ['project.task']

    @api.multi
    def get_access_action(self):
        """
        Override method that generated the link to access the document. Instead
        of the classic form view, redirect to the post on the website directly
        """
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'url': '/my/tasks/%s' % self.id,
            'target': 'self',
            'res_id': self.id,
        }
