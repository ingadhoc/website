##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from odoo.addons.google_account.models.google_service import TIMEOUT
import requests
import json
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
    # TODO borrar. Para no renegar con script de migra y por las dudas por ahora lo dejamos
    dont_show_childs = fields.Boolean(
    )
    title_view_type = fields.Selection([
        ('toc', 'Table Of Content'),
        ('kanban', 'Kanban'),
        ('invisible', 'Invisible'),
    ],
        default='toc',
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
            'context': {'default_parent_id': self.id},
        }

    def create_google_doc(self):
        self.ensure_one()
        template_id = self.env['ir.config_parameter'].sudo().get_param('website_doc.gdoc_template_id')
        if not template_id:
            raise ValidationError(_(
                "You need to create an ir.config_parameter with key 'website_doc.gdoc_template_id' and the google"
                " doc id of your template"))
        res_id = self.id
        res_model = self._name
        name_gdocs = 'Articulo: %s' % self.name
        google_web_base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        access_token = self.env['google.drive.config'].get_access_token()
        # Copy template in to drive with help of new access token
        request_url = "https://www.googleapis.com/drive/v2/files/%s?fields=parents/id&access_token=%s" % (
            template_id, access_token)
        headers = {"Content-type": "application/x-www-form-urlencoded"}
        try:
            req = requests.get(request_url, headers=headers, timeout=TIMEOUT)
            req.raise_for_status()
            parents_dict = req.json()
        except requests.HTTPError:
            raise UserError(_("The Google Template cannot be found. Maybe it has been deleted."))

        record_url = "Click on link to open Record in Odoo\n %s/?db=%s#id=%s&model=%s" % (
            google_web_base_url, self._cr.dbname, res_id, res_model)
        data = {
            "title": name_gdocs,
            "description": record_url,
            "parents": parents_dict['parents']
        }
        request_url = "https://www.googleapis.com/drive/v2/files/%s/copy?access_token=%s" % (template_id, access_token)
        headers = {
            'Content-type': 'application/json',
            'Accept': 'text/plain'
        }
        # resp, content = Http().request(request_url, "POST", data_json, headers)
        req = requests.post(request_url, data=json.dumps(data), headers=headers, timeout=TIMEOUT)
        req.raise_for_status()
        content = req.json()
        res = {}
        if content.get('alternateLink'):
            self.google_doc_code = content['id']
            res['id'] = self.env["ir.attachment"].create({
                'res_model': res_model,
                'name': name_gdocs,
                'res_id': res_id,
                'type': 'url',
                'url': content['alternateLink']
            }).id
