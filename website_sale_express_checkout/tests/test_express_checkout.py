##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo.addons.l10n_ar.tests.common import TestArCommon
from odoo.addons.website_sale.tests.common import MockRequest
from odoo.addons.website_sale_express_checkout.controllers.main import (
    WebsiteSaleExpressCheckout,
)
from odoo.tests import tagged

DELIVERY_HREF = "/shop/checkout"
EXTRA_HREF = "/shop/extra_info"
EXPRESS_HREF = "/shop/express_checkout"


@tagged("post_install_l10n", "post_install", "-at_install")
class TestExpressCheckout(TestArCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ar_company = cls.company_data["company"]
        cls.website = cls.env["website"].create(
            {
                "name": "AR Express Website",
                "company_id": cls.ar_company.id,
            }
        )
        cls.controller = WebsiteSaleExpressCheckout()
        cls.res_CF = cls.env.ref("l10n_ar.res_CF")
        cls.res_IVARI = cls.env.ref("l10n_ar.res_IVARI")
        cls.res_IVAE = cls.env.ref("l10n_ar.res_IVAE")
        cls.it_cuit = cls.env.ref("l10n_ar.it_cuit")
        cls.it_dni = cls.env.ref("l10n_ar.it_dni")

    # ------------------------------------------------------------------
    # Steps (model level, no request)
    # ------------------------------------------------------------------
    def test_steps_disabled_is_standard(self):
        """Default flag False -> delivery/extra published, express not."""
        self.assertFalse(self.website.enable_express_checkout)
        self.assertTrue(self.website._get_checkout_step(DELIVERY_HREF).is_published)
        self.assertFalse(self.website._get_checkout_step(EXPRESS_HREF).is_published)

    def test_steps_toggle_publishes_express(self):
        self.website.enable_express_checkout = True
        self.assertTrue(self.website._get_checkout_step(EXPRESS_HREF).is_published)
        self.assertFalse(self.website._get_checkout_step(DELIVERY_HREF).is_published)
        self.assertFalse(self.website._get_checkout_step(EXTRA_HREF).is_published)
        # Disabling restores the native steps.
        self.website.enable_express_checkout = False
        self.assertFalse(self.website._get_checkout_step(EXPRESS_HREF).is_published)
        self.assertTrue(self.website._get_checkout_step(DELIVERY_HREF).is_published)

    def test_enabling_sets_background_post(self):
        self.ar_company.website_sale_background_post = False
        self.website.enable_express_checkout = True
        self.assertTrue(self.ar_company.website_sale_background_post)

    # ------------------------------------------------------------------
    # AR-only guard
    # ------------------------------------------------------------------
    def test_ar_only_guard(self):
        self.website.enable_express_checkout = True
        cart = (
            self.env["sale.order"]
            .sudo()
            .create(
                {
                    "partner_id": self.partner.id,
                    "company_id": self.ar_company.id,
                    "website_id": self.website.id,
                }
            )
        )
        self.assertTrue(self.controller._express_checkout_enabled(cart))
        self.website.enable_express_checkout = False
        self.assertFalse(self.controller._express_checkout_enabled(cart))

    # ------------------------------------------------------------------
    # Payload hardening: derived fields are discarded (forged POST, C2)
    # ------------------------------------------------------------------
    def test_parse_form_data_discards_derived_fields(self):
        forged = {
            "name": "Foo",
            "email": "foo@example.com",
            "l10n_ar_afip_responsibility_type_id": str(self.res_IVARI.id),
            "l10n_latam_identification_type_id": str(self.it_cuit.id),
        }
        with MockRequest(self.env, website=self.website) as request:
            request.express_checkout_flow = True
            request.express_checkout_factura_a = False
            address_values, _extra = self.controller._parse_form_data(forged)
        self.assertNotIn("l10n_ar_afip_responsibility_type_id", address_values)
        self.assertNotIn("l10n_latam_identification_type_id", address_values)
        self.assertEqual(address_values.get("name"), "Foo")

    def test_parse_form_data_derives_id_type_from_document(self):
        # CF: the id type is derived from the document shape (not trusted from the
        # form) and set alongside the vat — a DNI-length number -> it_dni.
        with MockRequest(self.env, website=self.website) as request:
            request.express_checkout_flow = True
            request.express_checkout_factura_a = False
            dni_values, _e = self.controller._parse_form_data({"name": "Foo", "vat": "12345678"})
            cuit_values, _e = self.controller._parse_form_data({"name": "Bar", "vat": "30712345671"})
        self.assertEqual(dni_values.get("l10n_latam_identification_type_id"), self.it_dni.id)
        self.assertEqual(cuit_values.get("l10n_latam_identification_type_id"), self.it_cuit.id)

    # ------------------------------------------------------------------
    # Server-side tax derivation (C6) — via _express_apply_tax_identity
    # ------------------------------------------------------------------
    def _apply_identity(self, factura_a=False, vat=False, id_type=None, responsibility=None):
        vals = {"name": "Comprador"}
        if id_type:
            vals["l10n_latam_identification_type_id"] = id_type.id
        if vat:
            vals["vat"] = vat
        if responsibility:
            vals["l10n_ar_afip_responsibility_type_id"] = responsibility.id
        partner = self.env["res.partner"].sudo().create(vals)
        with MockRequest(self.env, website=self.website) as request:
            request.express_checkout_flow = True
            request.express_checkout_factura_a = factura_a
            self.controller._express_apply_tax_identity(partner, factura_a)
        return partner

    def test_derive_cf_without_document(self):
        partner = self._apply_identity()
        self.assertEqual(partner.l10n_ar_afip_responsibility_type_id, self.res_CF)
        self.assertEqual(partner.l10n_latam_identification_type_id, self.it_dni)
        self.assertEqual(partner.country_id, self.env.ref("base.ar"))

    def test_derive_cf_with_cuit_shaped_document(self):
        partner = self._apply_identity(vat="30712345671", id_type=self.it_cuit)
        self.assertEqual(partner.l10n_latam_identification_type_id, self.it_cuit)
        self.assertEqual(partner.l10n_ar_afip_responsibility_type_id, self.res_CF)

    def test_factura_a_sets_cuit_keeps_form_responsibility(self):
        # Factura A: id type is forced to CUIT; the responsibility comes from the
        # form (here Exento) and is NOT overwritten with a default.
        partner = self._apply_identity(factura_a=True, responsibility=self.res_IVAE)
        self.assertEqual(partner.l10n_latam_identification_type_id, self.it_cuit)
        self.assertEqual(partner.l10n_ar_afip_responsibility_type_id, self.res_IVAE)

    def test_existing_responsibility_not_overwritten(self):
        # C9: a partner that already is Responsable Inscripto must not be degraded.
        partner = self._apply_identity(factura_a=False, responsibility=self.res_IVARI)
        self.assertEqual(partner.l10n_ar_afip_responsibility_type_id, self.res_IVARI)

    def test_complete_address_values_sets_country_no_tax(self):
        values = {"street": "Av. Siempreviva 742"}
        cart = (
            self.env["sale.order"]
            .sudo()
            .create(
                {
                    "partner_id": self.partner.id,
                    "company_id": self.ar_company.id,
                    "website_id": self.website.id,
                }
            )
        )
        with MockRequest(self.env, website=self.website) as request:
            request.express_checkout_flow = True
            self.controller._complete_address_values(values, "delivery", False, order_sudo=cart)
        self.assertEqual(values["country_id"], self.env.ref("base.ar").id)
        self.assertNotIn("l10n_ar_afip_responsibility_type_id", values)
