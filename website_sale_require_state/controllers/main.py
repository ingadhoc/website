##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo import http
from odoo.http import request


class WebsiteSaleRequiredState(WebsiteSale):

    def _get_mandatory_billing_fields(self):
        return ["name", "email", "street", "city", "country_id", "state_id", "zip"]
    
    def _get_mandatory_shipping_fields(self):
        return ["name", "street", "city", "country_id", "state_id", "zip"]
