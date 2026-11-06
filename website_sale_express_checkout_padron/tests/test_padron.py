##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from unittest.mock import patch

from odoo.addons.l10n_ar.tests.common import TestArCommon
from odoo.addons.website_sale.tests.common import MockRequest
from odoo.addons.website_sale_express_checkout_padron.controllers.main import (
    WebsiteSaleExpressCheckout as PadronController,
)
from odoo.exceptions import UserError
from odoo.tests import tagged
from odoo.tools import mute_logger

_PADRON_METHOD = "get_data_from_padron_afip"
_PADRON_LOGGER = "odoo.addons.website_sale_express_checkout_padron.controllers.main"
# A valid CUIT (check digit) so the endpoint runs the query instead of bailing out.
_VALID_CUIT = "30712345671"


@tagged("post_install_l10n", "post_install", "-at_install")
class TestExpressCheckoutPadronLookup(TestArCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.website = cls.env["website"].create(
            {
                "name": "AR Padron Website",
                "company_id": cls.company_data["company"].id,
            }
        )
        cls.controller = PadronController()
        cls.res_RM = cls.env.ref("l10n_ar.res_RM")

    def _lookup(self, vat):
        with MockRequest(self.env, website=self.website):
            return self.controller._express_padron_lookup(vat=vat)

    def test_lookup_success(self):
        padron = {
            "name": "ACME SA",
            "street": "Av. Corrientes 1234",
            "city": "CABA",
            "zip": "C1043",
            "l10n_ar_afip_responsibility_type_id": self.res_RM.id,
        }
        with patch.object(self.registry["res.partner"], _PADRON_METHOD, return_value=padron):
            res = self._lookup(_VALID_CUIT)
        self.assertTrue(res["available"])
        self.assertTrue(res["found"])
        self.assertEqual(res["values"]["l10n_ar_afip_responsibility_type_id"], self.res_RM.id)
        self.assertEqual(res["values"]["name"], "ACME SA")

    @mute_logger(_PADRON_LOGGER)
    def test_lookup_usererror_is_manual(self):
        with patch.object(self.registry["res.partner"], _PADRON_METHOD, side_effect=UserError("no certificate")):
            res = self._lookup(_VALID_CUIT)
        self.assertTrue(res["available"])
        self.assertFalse(res["found"])

    @mute_logger(_PADRON_LOGGER)
    def test_lookup_timeout_is_manual(self):
        with patch.object(self.registry["res.partner"], _PADRON_METHOD, side_effect=TimeoutError("ws timeout")):
            res = self._lookup(_VALID_CUIT)
        self.assertFalse(res["found"])

    def test_lookup_partial_returns_found_with_values(self):
        # ARCA answered with fiscal data but no responsibility: still found=True,
        # with the values it did return. The client locks those and leaves the
        # empty fields (e.g. the responsibility) editable — never blocked.
        with patch.object(
            self.registry["res.partner"],
            _PADRON_METHOD,
            return_value={"name": "ACME", "street": "Av. Corrientes 1234"},
        ):
            res = self._lookup(_VALID_CUIT)
        self.assertTrue(res["found"])
        self.assertEqual(res["values"]["name"], "ACME")
        self.assertNotIn("l10n_ar_afip_responsibility_type_id", res["values"])

    def test_lookup_invalid_cuit_does_not_query(self):
        with patch.object(self.registry["res.partner"], _PADRON_METHOD) as mocked:
            res = self._lookup("123")
            mocked.assert_not_called()
        self.assertFalse(res["found"])

    def test_timeout_param_default(self):
        with MockRequest(self.env, website=self.website):
            self.assertEqual(self.controller._express_padron_timeout(), 8.0)
        self.env["ir.config_parameter"].sudo().set_param("website_sale_express_checkout.padron_timeout", "3.5")
        with MockRequest(self.env, website=self.website):
            self.assertEqual(self.controller._express_padron_timeout(), 3.5)
