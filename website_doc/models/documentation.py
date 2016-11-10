# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, fields, api
from openerp.osv import osv


class Documentation(models.Model):
    _name = 'website.doc.toc'
    _description = 'Documentation ToC'
    _inherit = ['website.seo.metadata']
    _order = "sequence, parent_left"
    _parent_order = "sequence, name"
    _parent_store = True

    def name_get(self, cr, uid, ids, context=None):
        if isinstance(ids, (list, tuple)) and not len(ids):
            return []
        if isinstance(ids, (long, int)):
            ids = [ids]
        reads = self.read(
            cr, uid, ids, ['name', 'parent_id'],
            context=context)
        res = []
        for record in reads:
            name = record['name']
            if record['parent_id']:
                name = record['parent_id'][1]+' / '+name
            res.append((record['id'], name))
        return res

    # TODO master remove me
    def _name_get_fnc(
            self, cr, uid, ids,
            prop, unknow_none, context=None):
        res = self.name_get(cr, uid, ids, context=context)
        return dict(res)

    sequence = fields.Integer(
        'Sequence',
        default=10,
        )
    name = fields.Char(
        'Name',
        required=True,
        # to avoid complications we disable translation
        # translate=True,
        )
    parent_id = fields.Many2one(
        'website.doc.toc',
        'Parent Table Of Content',
        ondelete='cascade',
        domain=[('is_article', '=', False)],
        )
    child_ids = fields.One2many(
        'website.doc.toc',
        'parent_id',
        'Children Table Of Content'
        )
    parent_left = fields.Integer(
        'Left Parent',
        select=True
        )
    parent_right = fields.Integer(
        'Right Parent',
        select=True
        )
    is_article = fields.Boolean(
        'Is Article?'
        )
    article_toc_id = fields.Many2one(
        'website.doc.toc',
        'Documentation ToC',
        ondelete='set null',
        domain=[('is_article', '=', False)],
        )
    article_ids = fields.One2many(
        'website.doc.toc',
        'article_toc_id',
        'Articles',
        domain=[('is_article', '=', True)],
        context={'default_is_article': 1},
        )
    add_google_doc = fields.Boolean(
        'Add Google Doc?',
        help="Add Google Doc after Page Content?"
        )
    google_doc_link = fields.Char(
        'Google Document Code',
        )
    google_doc_code = fields.Char(
        'Google Document Code',
        )
    google_doc_height = fields.Char(
        'Google Document Height',
        default='1050px'
        )
    content = fields.Html(
        'Content',
        )
    google_doc = fields.Text(
        'Content',
        compute='_get_google_doc',
        )
    group_ids = fields.Many2many(
        'res.groups',
        'website_doc_toc_group_rel',
        'website_toc_id', 'gid', 'Groups',
        help="If you have groups, "
             "the visibility of this TOC will "
             "be based on these groups. "
        # "If this field is empty, Odoo will compute
        # visibility based on the "
        # related object's read access."
        )
    state = fields.Selection(
        [('private', 'Is Private'),
         ('published', 'Published')],
        'State',
        required=True,
        default='private',
        # default='private',
        help="If private, then it wont be accesible "
             "by portal or public users"
        )
    partner_id = fields.Many2one(
        'res.partner',
        'Partner',
        help='If partner is set, only this partner will be able\
        to see this item (except documentation managers)',
        )

    @api.one
    @api.depends('google_doc_code', 'google_doc_height')
    def _get_google_doc(self):
        self.google_doc = False
        if self.google_doc_height and self.google_doc_code:
            google_doc = google_doc_template % (
                self.google_doc_height, self.google_doc_code)
        self.google_doc = google_doc

    _constraints = [
        (osv.osv._check_recursion,
            'Error ! You cannot create recursive categories.', ['parent_id'])
    ]

google_doc_template = """
 <div class="row">
    <iframe id="google-doc-iframe" srcdoc="" style="height: %s; margin:
     0 auto; padding-left: 20px; padding-right: 20px" align="middle"
     frameborder="0" width="100%%" height="300" scrolling="no">
    </iframe>

    <script src="//ajax.googleapis.com/ajax/libs/jquery/2.1.1/jquery.min.js">
    </script>
    <script>
    $(function() {
        $.get("https://docs.google.com/document/d/%s/pub?", function(html) {
            $("#google-doc-iframe").attr("srcdoc", html);
            setTimeout(function() {
                $("#google-doc-iframe").contents().find(
                'a[href^="http://"]').attr("target", "_blank");
                $("#google-doc-iframe").contents().find(
                'a[href^="https://"]').attr("target", "_blank");
            }, 1000);
        });
    });
    </script>
</div>
"""
