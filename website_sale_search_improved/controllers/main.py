##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.http import request
from odoo.osv import expression


def new_get_search_domain(self, search, category, attrib_values, search_in_description=True):
    """ Monkey patch instead of overwriting method to allow others inheriting
    this method
    """
    # TODO ver si usamos modulo de la oca de buscar por atributos
    # tambien pdoemos ver si cambiamos logica de que filtre como hace
    # vauxoo cambiando la parte de attrib_values comparando con or
    domains = [request.website.sale_product_domain()]
    if search:
        domains.append(request.env['product.template']._search_smart_search('ilike', search))

    if category:
        domains.append([('public_categ_ids', 'child_of', int(category))])

    if attrib_values:
        attrib = None
        ids = []
        for value in attrib_values:
            if not attrib:
                attrib = value[0]
                ids.append(value[1])
            elif value[0] == attrib:
                ids.append(value[1])
            else:
                domains.append([('attribute_line_ids.value_ids', 'in', ids)])
                attrib = value[0]
                ids = [value[1]]
        if attrib:
            domains.append([('attribute_line_ids.value_ids', 'in', ids)])

    return expression.AND(domains)


WebsiteSale._get_search_domain = new_get_search_domain
