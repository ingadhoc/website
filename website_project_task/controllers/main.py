##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import http
from odoo.addons.website_portal.controllers.main import website_account
from odoo.http import request


class WebsiteAccount(website_account):

    @http.route()
    def account(self):
        response = super(WebsiteAccount, self).account()
        # lo cambiamos para que sea como sugieren aca porque si no se
        # ven tareas que el usuario no tiene permisos
        # user = request.env.user
        # TDE FIXME: shouldn't that be mnaged by the access rule itself ?
        # portal projects where you or someone from your company are a follower
        # project_tasks = request.env['project.task'].sudo().search([
        #     '&',
        #     ('project_id.privacy_visibility', '=', 'portal'),
        #     '|',
        #     ('message_partner_ids', 'child_of', [
        #         user.partner_id.commercial_partner_id.id]),
        #     ('message_partner_ids', 'child_of', [user.partner_id.id])
        # ])
        project_tasks = request.env['project.task'].search([])
        response.qcontext.update({'tasks': project_tasks})
        return response


class WebsiteProjectIssue(http.Controller):
    @http.route([
        '/my/tasks/<int:task_id>'], type='http', auth="user", website=True)
    def issues_followup(self, task_id=None):
        task = request.env['project.task'].browse(task_id)
        return request.website.render(
            "website_project_task.tasks_followup", {'task': task})
