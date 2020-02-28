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
    article_type = fields.Selection([
        ('webpage', 'Web Page'),
        ('google_doc', 'Google Doc'),
        ('url', 'URL'),
    ],
        string='Articule Type',
        default='webpage',
    )
    article_url = fields.Char(
        'Article URL',
    )
    google_doc_code = fields.Char(
        'Google Document Code',
    )
    content = fields.Html(
        'Content',
        sanitize=False,
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
                rec.message_post(body=_('Contenido actualizado'))
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
                        ' padres no publicados. Doc id %s ("%s"), parents ids %s') % (
                            rec.id, rec.name, parents_not_published.ids))
            elif rec.state == 'portal':
                parents_private = rec.search([
                    ('id', 'parent_of', rec.id), ('state', '=', 'private')])
                if parents_private:
                    raise ValidationError(_(
                        'No puede publicar este articulo porque hay articulos'
                        ' padres privados. Doc id %s ("%s"), parents ids %s') % (
                            rec.id, rec.name, parents_private.ids))
                childs_published = rec.search([
                    ('id', 'child_of', rec.id), ('state', '=', 'published')])
                if childs_published:
                    raise ValidationError(_(
                        'No puede pasar a portal este articulo porque hay '
                        ' publicados. Doc id %s ("%s"), childs ids %s') % (rec.id, rec.name, childs_published.ids))
            else:
                childs_published = rec.search([
                    ('id', 'child_of', rec.id), ('state', '!=', 'private')])
                if childs_published:
                    raise ValidationError(_(
                        'No puede despublicr este articulo porque hay hijos'
                        ' publicados. Doc id %s ("%s"), childs ids %s') % (rec.id, rec.name, childs_published.ids))

    @api.multi
    def _get_doc_status(self):
        self.ensure_one()
        return self.env['website.doc.status'].search(
            [('user_id', '=', self._uid), ('article_doc_id', '=', self.id)],
            limit=1)

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
