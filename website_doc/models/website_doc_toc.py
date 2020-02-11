##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)


class WebsiteDocToc(models.Model):
    _name = 'website.doc.toc'
    _description = 'Documentation ToC'
    _inherit = ['website.seo.metadata', 'mail.thread', 'mail.activity.mixin']
    _order = "sequence, parent_path"
    _parent_order = "sequence, name"
    _parent_store = True

    sequence = fields.Integer(
        default=10,
    )
    name = fields.Char(
        required=True,
        # to avoid complications we disable translation
        # translate=True,
        index=True,
    )
    parent_id = fields.Many2one(
        'website.doc.toc',
        'Parent Table Of Content',
        ondelete='cascade',
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
    parent_path = fields.Char(
        index=True
    )
    is_article = fields.Boolean(
        'Is Article?',
        index=True,
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
        help="Add Google Doc after Page Content?",
    )
    google_doc_link = fields.Char(
        'Google Document Link',
    )
    google_doc_code = fields.Char(
        'Google Document Code',
    )
    google_doc_height = fields.Char(
        'Google Document Height',
        default='1050px',
    )
    content = fields.Html(
        'Content',
        sanitize=False,
    )
    google_doc = fields.Text(
        'Google Content',
        compute='_compute_google_doc',
    )
    state = fields.Selection([
        ('private', 'Is Private'),
        ('portal', 'Portal'),
        ('published', 'Published'),
    ],
        'State',
        required=True,
        help="If private, then it wont be accesible "
             "by portal or public users",
        index=True,
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
        'http://fontawesome.io/icons/, for eg. "fa-pencil-square-o"',
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

    @api.model
    def default_get(self, fields):
        vals = super().default_get(fields)
        if not self._context.get('from_copy'):
            vals['state'] = 'private'
        return vals

    @api.multi
    def copy(self, default=None):
        return super(WebsiteDocToc, self.with_context(from_copy=True)).copy(default=default)

    @api.multi
    def write(self, vals):
        if 'content' in vals:
            for rec in self:
                rec.message_post(body='Contenido actualizado')
        return super().write(vals)

    @api.constrains('state')
    def check_published(self):
        for rec in self:
            if rec.state == 'published':
                parents_not_published = rec.search([
                    ('id', 'parent_of', rec.id), ('state', '!=', 'published')])
                if parents_not_published:
                    raise ValidationError(_(
                        'No puede publicar este articulo porque hay articulos'
                        ' padres no publicados'))
            elif rec.state == 'portal':
                parents_private = rec.search([
                    ('id', 'parent_of', rec.id), ('state', '=', 'private')])
                if parents_private:
                    raise ValidationError(_(
                        'No puede publicar este articulo porque hay articulos'
                        ' padres privados'))
                childs_published = rec.search([
                    ('id', 'child_of', rec.id), ('state', '=', 'published')])
                if childs_published:
                    raise ValidationError(_(
                        'No puede pasar a portal este articulo porque hay '
                        ' publicados'))
            else:
                childs_published = rec.search([
                    ('id', 'child_of', rec.id), ('state', '!=', 'private')])
                if childs_published:
                    raise ValidationError(_(
                        'No puede despublicr este articulo porque hay hijos'
                        ' publicados'))

    @api.multi
    def _get_doc_status(self):
        self.ensure_one()
        return self.env['website.doc.status'].search(
            [('user_id', '=', self._uid), ('article_doc_id', '=', self.id)],
            limit=1)

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
            rec.read_status = True if rec._get_doc_status() else False

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

    @api.depends('google_doc_code', 'google_doc_height')
    def _compute_google_doc(self):
        for rec in self:
            rec.google_doc = False
            if rec.google_doc_height and rec.google_doc_code:
                google_doc = google_doc_template % (
                    rec.google_doc_height, rec.google_doc_code)
                rec.google_doc = google_doc

    @api.constrains('parent_id')
    def _check_parent_id(self):
        if not self._check_recursion():
            raise ValidationError(
                _('Error! You cannot create recursive categories.'))

    @api.multi
    def action_open_childs(self):
        return {
            'name': _('Childs TOC'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': self._name,
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('parent_id', '=', self.id)],
        }


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
