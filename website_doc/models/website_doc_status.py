##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields


class DocumentationStatusDoc(models.Model):
    _name = 'website.doc.status'
    _description = 'Documentation Status'

    user_id = fields.Many2one(
        'res.users',
        'User',
        index=True,
    )
    article_doc_id = fields.Many2one(
        'website.doc.toc',
        'Article',
        required=True,
        ondelete='cascade',
        auto_join=True,
        index=True,
    )
