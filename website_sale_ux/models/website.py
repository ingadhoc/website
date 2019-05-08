##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, tools


class Website(models.Model):
    _inherit = 'website'

    # TODO Remove in V12
    # This method is cached, must not return records! See also #8795
    @tools.ormcache(
        'self.env.uid', 'country_code', 'show_visible', 'website_pl',
        'current_pl', 'all_pl', 'partner_pl', 'order_pl')
    def _get_pl_partner_order(
            self, country_code, show_visible, website_pl, current_pl, all_pl,
            partner_pl=False, order_pl=False):
        """ Return the list of pricelists that can be used on website for
         the current user.
        :param str country_code: code iso or False, If set,
         we search only price list available for this country
        :param bool show_visible: if True, we don't display pricelist
         where selectable is False (Eg: Code promo)
        :param int website_pl: The default pricelist used on this website
        :param int current_pl: The current pricelist used on the website
                               (If not selectable but the current pricelist
                               we had this pricelist anyway)
        :param list all_pl: List of all pricelist available for this website
        :param int partner_pl: the partner pricelist
        :param int order_pl: the current cart pricelist
        :returns: list of pricelist ids
        """
        pricelists = self.env['product.pricelist']
        if country_code:
            for cgroup in self.env['res.country.group'].search(
                    [('country_ids.code', '=', country_code)]):
                for group_pricelists in cgroup.pricelist_ids:
                    if not show_visible or group_pricelists.selectable\
                            or group_pricelists.id in (current_pl, order_pl):
                        pricelists |= group_pricelists

        partner = self.env.user.partner_id
        partner = partner.sudo(user=self.env.user)
        is_public = self.user_id.id == self.env.user.id
        if not is_public and(
                not
                pricelists or(
                    partner_pl or partner.property_product_pricelist.id) !=
                website_pl):
            if partner.property_product_pricelist.website_id:
                pricelists |= partner.property_product_pricelist

        if not pricelists:  # no pricelist for this country, or no GeoIP
            pricelists |= all_pl.filtered(
                lambda pl: not show_visible or pl.selectable or pl.id
                in (current_pl, order_pl))
        if not show_visible and not country_code:
            pricelists |= all_pl.filtered(lambda pl: pl.sudo().code)

        # This method is cached, must not return records! See also #8795
        return pricelists.ids
