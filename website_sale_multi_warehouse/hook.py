from odoo import SUPERUSER_ID, api


def pre_init_hook(cr):
    env = api.Environment(cr, SUPERUSER_ID, {})
    websites = env["website"].search([])
    websites.write({"warehouse_id": False})
