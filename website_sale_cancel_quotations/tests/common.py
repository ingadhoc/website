##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import fields
from odoo.addons.sale_ux.tests.common import SaleUxCommon

CANCEL_BACKOFFICE = "sale_ux.cancel_old_quotations"
CANCEL_WEBSITE = "website_sale_ux.cancel_old_website_quotations"
DAYS_TO_KEEP = "sale_ux.days_to_keep_quotations"


class WebsiteSaleCancelQuotationsCommon(SaleUxCommon):
    """Scenario configuration for the two switches this module coordinates.

    Environment (accounts, taxes) comes from SaleUxCommon; the website the
    scenario needs is created here, and every quotation is created by the test
    itself so no order already living in the database can relax an assert.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.website = cls.env["website"].create({"name": "Cancel Quotations Test Website"})

    @classmethod
    def _create_old_quotation(cls, days_old, website=False):
        """A quotation dated ``days_old`` days ago, on the website or not."""
        values = {"date_order": fields.Datetime.subtract(fields.Datetime.now(), days=days_old)}
        if website:
            values["website_id"] = cls.website.id
        return cls._create_sale_order(**values)

    def _set_switches(self, backoffice, website):
        """Store both switches the way the Settings page does.

        A ticked box writes the parameter; an unticked one removes it, because
        set_param unlinks falsy values.
        """
        self.IrConfig.set_param(CANCEL_BACKOFFICE, "True" if backoffice else False)
        self.IrConfig.set_param(CANCEL_WEBSITE, "True" if website else False)

    def _build_scenario(self):
        """Every combination runs over the same cast, created from scratch.

        Two expired quotations to be told apart, plus two that no combination
        may ever touch: a recent one and an already confirmed one.
        """
        scenario = {
            "expired_backoffice": self._create_old_quotation(days_old=20),
            "expired_website": self._create_old_quotation(days_old=20, website=True),
            "recent_website": self._create_old_quotation(days_old=2, website=True),
            "confirmed_website": self._create_old_quotation(days_old=20, website=True),
        }
        # Placed directly in state: what is under test is the domain of the
        # cron, not the confirmation flow, which depends on the module stack
        scenario["confirmed_website"].state = "sale"
        scenario["universe"] = (
            scenario["expired_backoffice"]
            | scenario["expired_website"]
            | scenario["recent_website"]
            | scenario["confirmed_website"]
        )
        return scenario
