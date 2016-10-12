# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, api

import logging
_logger = logging.getLogger(__name__)


class Website(models.Model):
    _inherit = 'website'

    @api.multi
    def sale_get_order(
            self, force_create=False, code=None, update_pricelist=None):
        return super(Website, self.with_context(
            default_order_policy='prepaid')).sale_get_order(
                force_create=force_create,
                code=code,
                update_pricelist=update_pricelist)
