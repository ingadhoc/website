from odoo import api, models


class Http(models.AbstractModel):
    _inherit = "ir.http"

    @api.model
    def get_frontend_session_info(self):
        session_info = super(Http, self).get_frontend_session_info()
        session_info.update(
            {
                "website_hide_all_prices": self.env.website.website_hide_all_prices,
            }
        )
        return session_info
