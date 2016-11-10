# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models

import logging
_logger = logging.getLogger(__name__)


class Website(models.Model):
    _inherit = 'website'

    def sale_get_order(
            self, cr, uid, ids, force_create=False,
            code=None, update_pricelist=None, context=None):
        if not context:
            context = {}
        context = context.copy()
        context['default_order_policy'] = 'prepaid'
        return super(Website, self).sale_get_order(
            cr, uid, ids,
            force_create=force_create,
            code=code,
            update_pricelist=update_pricelist,
            context=context)
