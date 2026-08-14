from odoo import http
from odoo.addons.web.controllers.binary import Binary
from odoo.addons.website_sale.controllers import main
from odoo.tools.translate import _


class WebsiteSale(main.WebsiteSale):
    def _get_shop_payment_values(self, order, **kwargs):
        payment_values = super()._get_shop_payment_values(order=order, **kwargs)
        payment_values["submit_button_label"] = _("Complete Purchase")
        return payment_values

    def _prepare_address_form_values(self, order_sudo, partner_sudo, address_type, **kwargs):
        rendering_values = super()._prepare_address_form_values(
            order_sudo, partner_sudo, address_type=address_type, **kwargs
        )
        website = http.request.website.sudo()
        allowed_countries = website.checkout_country_ids
        if not allowed_countries:
            return rendering_values

        rendering_values["countries"] = allowed_countries
        country = rendering_values.get("country")
        if country not in allowed_countries:
            # The standard default (GeoIP, with the public user's country as fallback) is
            # not reliable when the shop sells to a restricted set of countries: behind a
            # proxy the geolocated country can be plain wrong for every visitor.
            company_country = website.company_id.country_id
            country = company_country if company_country in allowed_countries else allowed_countries[0]
            address_fields = country.get_address_fields()
            rendering_values.update(
                {
                    "country": country,
                    "country_states": country.state_ids,
                    "zip_before_city": (
                        "zip" in address_fields and address_fields.index("zip") < address_fields.index("city")
                    ),
                }
            )
        return rendering_values


class WebsiteBinary(Binary):
    @http.route()
    def content_image(
        self,
        xmlid=None,
        model="ir.attachment",
        id=None,
        field="raw",
        filename_field="name",
        filename=None,
        mimetype=None,
        unique=False,
        download=False,
        width=0,
        height=0,
        crop=False,
        access_token=None,
        nocache=False,
    ):
        """
        Eso es un Hack para que las imagenes de los productos en la web sean cacheables por los proxies
        por defecto las imagenes servidas tienen la cabecera Cache-Control: private, no-cache
        porque su acceso depende de los permisos del usuario con respecto al modelo.
        Cloudflare No cachea las imagenes tienen no-cache
        Presumimos que las imagenes de los productos son publicas y pueden ser cacheadas.
        Otro posible enfoque es agregar access_token a la URL pero no cumple con todo lo que necesitamos y
        los proxy no deberian cachear url con access_token
        """
        response = super().content_image(
            xmlid=xmlid,
            model=model,
            id=id,
            field=field,
            filename_field=filename_field,
            filename=filename,
            mimetype=mimetype,
            unique=unique,
            download=download,
            width=width,
            height=height,
            crop=crop,
            access_token=access_token,
            nocache=nocache,
        )
        website = http.request.env["website"].get_current_website()
        if (
            response.headers["Cache-Control"]
            and "private" in response.headers["Cache-Control"]
            and model == "product.template"
            and website
        ):
            cache_control = ", ".join(
                [x.strip() for x in response.headers["Cache-Control"].split(",") if x.strip() != "no-cache"]
            ).replace("private", "public")
            if cache_control:
                response.headers["Cache-Control"] = cache_control
            else:
                del response.headers["Cache-Control"]
        return response
