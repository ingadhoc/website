# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, fields, api, _
from openerp.osv import osv
from openerp.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)


class Documentation(models.Model):
    _name = 'website.doc.toc'
    _description = 'Documentation ToC'
    _inherit = ['website.seo.metadata']
    _order = "sequence, parent_left"
    _parent_order = "sequence, name"
    _parent_store = True

    sequence = fields.Integer(
        'Sequence',
        default=10,
    )
    name = fields.Char(
        'Name',
        required=True,
        # to avoid complications we disable translation
        # translate=True,
        index=True,
    )
    parent_id = fields.Many2one(
        'website.doc.toc',
        'Parent Table Of Content',
        # por ahora preferimos no perder y borrar todo por error
        ondelete='set null',
        # ondelete='cascade',
        domain=[('is_article', '=', False)],
        auto_join=True,
    )
    child_ids = fields.One2many(
        'website.doc.toc',
        'parent_id',
        'Children Table Of Content',
        copy=True,
        domain=[('is_article', '=', False)],
        auto_join=True,
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
    article_ids = fields.One2many(
        'website.doc.toc',
        'parent_id',
        'Articles',
        domain=[('is_article', '=', True)],
        context={'default_is_article': 1},
        copy=True,
        auto_join=True,
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
        sanitize=False,
    )
    google_doc = fields.Text(
        'Google Content',
        compute='_get_google_doc',
    )
    state = fields.Selection([
        ('private', 'Is Private'),
        ('portal', 'Portal'),
        ('published', 'Published'),
    ],
        'State',
        required=True,
        default='private',
        help="If private, then it wont be accesible "
             "by portal or public users"
    )
    dont_show_childs = fields.Boolean(
    )
    url_suffix = fields.Char(
        compute='_compute_url',
        compute_sudo=True,
    )
    documentation_id = fields.Many2one(
        'website.doc.toc',
        'Documentation',
        compute_sudo=True,
        compute='_compute_documentation',
        help='First documentation toc',
        # lo almacenamos para mejoras de performance
        store=True,
    )
    icon = fields.Char(
        help='fa-icon name, you can use any of the icons on '
        'http://fontawesome.io/icons/, for eg. "fa-pencil-square-o"'
    )
    read_status = fields.Boolean(
        'Read Status',
        compute='_compute_read',
        # inverse='_inverse_read'
    )
    reading_percentage = fields.Integer(
        'Reading percentage',
        compute="_compute_reading_percentage",
    )

    @api.constrains('state')
    def check_published(self):
        for rec in self:
            if rec.state == 'published':
                parents_not_published = rec.search([
                    ('id', 'parent_of', rec.id), ('state', '!=', 'published')])
                if parents_not_published:
                    raise UserError(_(
                        'No puede publicar este articulo porque hay articulos'
                        ' padres no publicados'))
            elif rec.state == 'portal':
                parents_private = rec.search([
                    ('id', 'parent_of', rec.id), ('state', '=', 'private')])
                if parents_private:
                    raise UserError(_(
                        'No puede publicar este articulo porque hay articulos'
                        ' padres privados'))
                childs_published = rec.search([
                    ('id', 'child_of', rec.id), ('state', '=', 'published')])
                if childs_published:
                    raise UserError(_(
                        'No puede pasar a portal este articulo porque hay '
                        ' publicados'))
            else:
                childs_published = rec.search([
                    ('id', 'child_of', rec.id), ('state', '!=', 'private')])
                if childs_published:
                    raise UserError(_(
                        'No puede despublicr este articulo porque hay hijos'
                        ' publicados'))

    @api.multi
    def _get_doc_status(self):
        self.ensure_one()
        domain = [('user_id', '=', self._uid)]
        return self.env['website.doc.status'].search(
            domain + [('article_doc_id', '=', self.id)], limit=1)

    @api.multi
    def _compute_reading_percentage(self):
        _logger.info('Computing reading percentage')
        for rec in self:
            child_articules = self.search(
                [('is_article', '=', True), ('id', 'child_of', rec.id)])
            if child_articules:
                total = len(child_articules)
                child_read = len(child_articules.filtered(
                    lambda p: p.read_status))
                rec.reading_percentage = int((
                    float(child_read) / float(total)) * 100)

    @api.multi
    def _compute_read(self):
        _logger.info('Computing read status')
        for rec in self:
            status = rec._get_doc_status()
            if status:
                rec.read_status = True
            else:
                rec.read_status = False

    # lo implementamos sin funcion inverse del campo porque si no requeria
    # que usuarios portal tengan permiso de escritura sobre este objeto si
    # bien era un dummy write
    @api.multi
    def inverse_read(self, read_status):
        status_obj = self.env['website.doc.status']
        for rec in self:
            status = rec._get_doc_status()
            if read_status and not status:
                vals = {
                    'user_id': rec._uid,
                    'article_doc_id': rec.id,
                }
                status_obj.create(vals)
            elif not read_status and status:
                status.unlink()

    # @api.multi
    # def _inverse_read(self):
    #     status_obj = self.env['website.doc.status']
    #     for rec in self:
    #         status = rec._get_doc_status()
    #         if rec.read_status and not status:
    #             vals = {
    #                 'user_id': rec._uid,
    #                 'article_doc_id': rec.id,
    #             }
    #             status_obj.create(vals)
    #         elif not rec.read_status and status:
    #             status.unlink()

    @api.multi
    # sacamos depends para que no de error con cache y newid
    # @api.depends('parent_id')
    def _compute_url(self):
        _logger.info('Computing doc urls')
        # uuid = self._context.get('uuid')
        for rec in self:
            rec.url_suffix = '/doc/%s/%s' % (rec.documentation_id.id, rec.id)
            # if uuid:
            #     rec.url_suffix = '%s/%s/%s' % (
            #         rec.url_suffix, uuid)

    @api.multi
    @api.depends('is_article', 'parent_id')
    def _compute_documentation(self):
        _logger.info('Computing documentation')
        for rec in self:
            # if rec.is_article:
            #     parent_toc = rec.article_toc_id
            # else:
            #     parent_toc = rec
            # the first parent is the documentation
            if not isinstance(rec.id, int):
                continue
            rec.documentation_id = rec.search([
                # ('id', 'parent_of', parent_toc.id),
                ('id', 'parent_of', rec.id),
                ('is_article', '=', False),
                ('parent_id', '=', False)], limit=1).id

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


class DocumentationStatusDoc(models.Model):
    _name = 'website.doc.status'
    _description = 'Documentation Status'

    user_id = fields.Many2one(
        'res.users',
        'User',
    )
    article_doc_id = fields.Many2one(
        'website.doc.toc',
        'Article',
        required=True,
        ondelete='cascade',
        auto_join=True,
    )
