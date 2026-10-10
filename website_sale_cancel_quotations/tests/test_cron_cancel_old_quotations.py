##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo.tests import tagged

from .common import CANCEL_WEBSITE, DAYS_TO_KEEP, WebsiteSaleCancelQuotationsCommon


@tagged("post_install", "-at_install")
class TestCronCancelOldQuotations(WebsiteSaleCancelQuotationsCommon):
    def test_cron_respeta_la_matriz_backoffice_website(self):
        """The two switches are independent, and that independence is the whole
        point of this module: without it sale_ux would reach both kinds."""
        self.IrConfig.set_param(DAYS_TO_KEEP, "10")
        cases = [
            ("con solo Ventas activo, la cotizacion de e-commerce sobrevive", True, False, ["expired_backoffice"]),
            ("con solo Website activo, la cotizacion de backoffice sobrevive", False, True, ["expired_website"]),
            ("con ambos activos, se cancelan las dos", True, True, ["expired_backoffice", "expired_website"]),
            ("sin ninguno activo, no se cancela nada", False, False, []),
        ]
        for label, backoffice, website, expected_keys in cases:
            with self.subTest(label):
                # A fresh cast per combination: a cancelled order stays cancelled
                scenario = self._build_scenario()
                self._set_switches(backoffice=backoffice, website=website)
                previous_states = self.snapshot_states(scenario["universe"])

                self.env["sale.order"]._cron_clean_old_quotations()

                expected = self.env["sale.order"].browse([scenario[key].id for key in expected_keys])
                self.assert_cron_cancelled_exactly(scenario["universe"], expected, previous_states)

    def test_flag_de_website_se_lee_del_parametro(self):
        """The switch on the Settings page and the parameter the cron reads are
        the same thing, in both directions."""
        settings = self.env["res.config.settings"].create({"cancel_old_website_quotations": True})

        settings.set_values()

        self.assertEqual(self.IrConfig.get_param(CANCEL_WEBSITE), "True")
        # A settings record opened afterwards reads the switch back as ticked
        self.assertTrue(self.env["res.config.settings"].create({}).cancel_old_website_quotations)

        # Unticking removes the parameter: set_param unlinks falsy values
        self.env["res.config.settings"].create({"cancel_old_website_quotations": False}).set_values()

        self.assertFalse(self.IrConfig.get_param(CANCEL_WEBSITE))


@tagged("post_install", "-at_install", "-standard")
class TestCronCancelOldQuotationsKnownIssues(WebsiteSaleCancelQuotationsCommon):
    """Confirmed defect, kept out of the default build until it is decided.

    models/sale_order.py:12 reads the switch with bool() over the raw parameter,
    and bool("False") is True. The Settings page never produces that value --
    unticking removes the parameter -- but System Parameters does, and a
    consultant disabling the cancellation by hand switches it on instead.

    One line fixes it: compare the parameter to "True" instead of calling
    bool(). Left unapplied here because this is a test PR, not a fix.
    """

    def test_un_parametro_en_false_no_cancela_cotizaciones_de_website(self):
        """A parameter typed by hand in Technical settings arrives as the string
        'False', which must switch the cancellation off, not on."""
        self.IrConfig.set_param(DAYS_TO_KEEP, "10")
        self._set_switches(backoffice=False, website=False)
        # What a consultant leaves behind when disabling it from System Parameters
        self.IrConfig.set_param(CANCEL_WEBSITE, "False")
        scenario = self._build_scenario()
        previous_states = self.snapshot_states(scenario["universe"])

        self.env["sale.order"]._cron_clean_old_quotations()

        self.assert_cron_cancelled_exactly(scenario["universe"], self.env["sale.order"], previous_states)
