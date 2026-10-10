from odoo.addons.website_sale_stock_variant_preselect.tests.common import VariantPreselectCommon
from odoo.tests import HttpCase, tagged


@tagged("post_install", "-at_install")
class TestCarouselTour(HttpCase, VariantPreselectCommon):
    """The configurator opened from a product carousel starts on the first variant with stock."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        snippet_filter = cls.env.ref("website_sale.dynamic_filter_newest_products")
        cls.env["website.page"].create(
            {
                "name": "Preselect carousel",
                "url": "/preselect-carousel",
                "type": "qweb",
                "key": "website_sale_stock_variant_preselect.test_carousel_page",
                "website_id": cls.website.id,
                "is_published": True,
                "arch": f"""
                    <t t-name="website_sale_stock_variant_preselect.test_carousel_page">
                        <t t-call="website.layout">
                            <div id="wrap">
                                <section data-snippet="s_dynamic_snippet_products"
                                    class="oe_website_sale s_dynamic_snippet_products s_dynamic"
                                    data-filter-id="{snippet_filter.id}"
                                    data-template-key="website_sale.dynamic_filter_template_product_product_products_item"
                                    data-product-category-id="all"
                                    data-product-names="{cls.product.name}"
                                    data-number-of-records="16">
                                    <div class="container">
                                        <div class="row">
                                            <section class="s_dynamic_snippet_content col">
                                                <div class="dynamic_snippet_template"/>
                                            </section>
                                        </div>
                                    </div>
                                </section>
                            </div>
                        </t>
                    </t>
                """,
            }
        )

    def test_carousel_opens_configurator_on_variant_with_stock(self):
        """Red is first in sequence but sold out: the configurator must open on Green."""
        self._add_product_qty_to_wh(self.green.id, 10, self.warehouse.lot_stock_id.id)

        self.start_tour("/preselect-carousel", "website_sale_stock_variant_preselect_carousel")
