from lxml import html as lxml_html
from odoo.addons.website_sale.tests.common import MockRequest, WebsiteSaleCommon
from odoo.tests import HttpCase, tagged


@tagged("post_install", "-at_install")
class TestTaxIndication(HttpCase, WebsiteSaleCommon):
    _test_user_groups = (
        "base.group_user",
        "base.group_system",
        "account.group_account_manager",
        "product.group_product_manager",
        "website.group_website_designer",
    )

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env.company.country_id = cls.env.ref("base.ar")
        cls.website.show_line_subtotals_tax_selection = "tax_included"
        cls.env.ref("website_sale.tax_indication").active = True

        TaxGroup = cls.env["account.tax.group"]
        cls.vat_21, cls.vat_10, cls.internal_tax = cls.env["account.tax"].create(
            [
                {
                    "name": "IVA 21%",
                    "amount": 21.0,
                    "tax_group_id": TaxGroup.create({"name": "IVA 21%", "l10n_ar_vat_afip_code": "5"}).id,
                },
                {
                    "name": "IVA 10.5%",
                    "amount": 10.5,
                    "tax_group_id": TaxGroup.create({"name": "IVA 10.5%", "l10n_ar_vat_afip_code": "4"}).id,
                },
                {
                    "name": "Impuesto Interno 8%",
                    "amount": 8.0,
                    "tax_group_id": TaxGroup.create({"name": "Internos"}).id,
                },
            ]
        )

        # Keep only the test product in the shop.
        cls.env["product.template"].search([("website_published", "=", True)]).website_published = False
        cls.ar_product = cls._create_product(
            name="AR Product",
            list_price=100.0,
            taxes_id=[(6, 0, (cls.vat_21 + cls.internal_tax).ids)],
        )

    def _get_vat_tax_names(self, fiscal_position=None):
        template = self.ar_product.product_tmpl_id
        fiscal_position = fiscal_position or self.env["account.fiscal.position"]
        with MockRequest(self.env, website=self.website) as request:
            prices = template._get_sales_prices(request.pricelist, fiscal_position, self.website)
            combination_info = template._get_additional_combination_info(
                product_or_template=self.ar_product,
                quantity=1.0,
                uom=self.ar_product.uom_id,
                website=self.website,
                pricelist=request.pricelist,
                fiscal_position=fiscal_position,
            )
        return prices[template.id]["l10n_ar_vat_tax_name"], combination_info["l10n_ar_vat_tax_name"]

    def test_vat_tax_name_only_vat(self):
        self.assertEqual(self._get_vat_tax_names(), ("IVA 21%", "IVA 21%"))

    def test_vat_tax_name_fiscal_position(self):
        fiscal_position = self.env["account.fiscal.position"].create({"name": "AR 10.5"})
        self.vat_10.write(
            {
                "fiscal_position_ids": [(6, 0, fiscal_position.ids)],
                "original_tax_ids": [(6, 0, self.vat_21.ids)],
            }
        )
        self.assertEqual(self._get_vat_tax_names(fiscal_position), ("IVA 10.5%", "IVA 10.5%"))

    def test_vat_tax_name_without_taxes(self):
        self.ar_product.taxes_id = False
        self.assertEqual(self._get_vat_tax_names(), ("", ""))

    def test_vat_tax_name_not_ar_website(self):
        self.env.company.country_id = self.country_us
        template = self.ar_product.product_tmpl_id
        with MockRequest(self.env, website=self.website) as request:
            prices = template._get_sales_prices(request.pricelist, self.env["account.fiscal.position"], self.website)
        self.assertNotIn("l10n_ar_vat_tax_name", prices[template.id])

    def _assert_legend(self, legend):
        for url in ("/shop", self.ar_product.website_url):
            html = self.url_open(url).text
            with self.subTest(url=url):
                if legend:
                    self.assertIn(legend, html)
                else:
                    self.assertNotIn("Excluded)", html)
                    self.assertNotIn("Included)", html)
                self.assertNotIn("(Tax included)", html)
                self.assertNotIn("(Tax excluded)", html)

    def test_legend_tax_included(self):
        self._assert_legend("(IVA 21% Included)")

    def test_legend_tax_excluded(self):
        self.website.show_line_subtotals_tax_selection = "tax_excluded"
        self._assert_legend("(+ IVA 21% Excluded)")

    def test_legend_pricelist_tax_display(self):
        pricelist = self._enable_pricelists()
        pricelist.tax_display = "tax_excluded"
        self._assert_legend("(+ IVA 21% Excluded)")

    def test_legend_view_inactive(self):
        self.env.ref("website_sale.tax_indication").active = False
        self._assert_legend(False)

    def test_legend_hidden_price(self):
        self.website.write({"prevent_sale": True, "prevent_sale_for": "zero_price"})
        self.ar_product.list_price = 0.0
        self.assertNotIn("Included)", self.url_open("/shop").text)
        # The product page renders the legend hidden with the price, so it shows up
        # when the customer picks a variant with a price.
        page = lxml_html.fromstring(self.url_open(self.ar_product.website_url).text)
        legend = page.xpath("//div[@name='product_price'][contains(@class, 'd-none')]//div[@name='tax_indicator']")
        self.assertEqual(len(legend), 1)
        self.assertIn("(IVA 21% Included)", legend[0].text_content())

    def test_legend_without_taxes(self):
        self.ar_product.taxes_id = False
        self._assert_legend(False)

    def test_legend_combo(self):
        combo = self.env["product.combo"].create(
            {
                "name": "Combo",
                "combo_item_ids": [(0, 0, {"product_id": self.ar_product.id})],
            }
        )
        self.ar_product.website_published = False
        combo_product = self._create_product(
            name="AR Combo",
            type="combo",
            list_price=100.0,
            combo_ids=[(6, 0, combo.ids)],
            taxes_id=[(6, 0, self.vat_21.ids)],
        )
        for url in ("/shop", combo_product.website_url):
            html = self.url_open(url).text
            with self.subTest(url=url):
                self.assertNotIn("Included)", html)
        self.assertIn("Taxes calculated at checkout.", html)

    def test_legend_not_ar_website(self):
        self.env.company.country_id = self.country_us
        self.website.show_line_subtotals_tax_selection = "tax_included"
        html = self.url_open(self.ar_product.website_url).text
        self.assertIn("(Tax included)", html)
        self.assertNotIn("IVA 21% Included)", html)
