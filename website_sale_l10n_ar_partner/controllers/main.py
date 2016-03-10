# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp.addons.website_sale.controllers.main import website_sale
from openerp import SUPERUSER_ID
from openerp.http import request


class WebsiteSale(website_sale):

    def _get_mandatory_billing_fields(self):
        mandatory_billing_fields = (
            super(WebsiteSale, self)._get_mandatory_billing_fields() +
            ['document_number', 'document_type_id'])
        return mandatory_billing_fields

    def checkout_values(self, data=None):
        cr, uid, context, registry = (
            request.cr, request.uid, request.context, request.registry)
        res = super(WebsiteSale, self).checkout_values(data)
        orm_document_types = registry.get('afip.document_type')
        document_type_ids = orm_document_types.search(
            cr, SUPERUSER_ID, [], context=context)
        document_types = orm_document_types.browse(
            cr, SUPERUSER_ID, document_type_ids, context)
        res.update({
            'document_types': document_types,
            })
        return res
# vim:expandtab:tabstop=4:softtabstop=4:shiftwidth=4:
