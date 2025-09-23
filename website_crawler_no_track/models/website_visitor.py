from odoo import models
from odoo.http import request


class WebsiteVisitor(models.Model):
    _inherit = "website.visitor"

    def _get_visitor_from_request(self, force_create=False, force_track_values=None):
        user_agent = request.httprequest.environ.get("HTTP_USER_AGENT")
        crawlers_names = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("website.crawlers_names", "OAI-SearchBot,crawler,Googlebot,Amazonbot,bingbot,PetalBot,AhrefsBot")
            .split(",")
        )
        if user_agent and any(crawler in user_agent for crawler in crawlers_names):
            return self.env["website.visitor"]

        return super()._get_visitor_from_request(force_create=force_create, force_track_values=force_track_values)
