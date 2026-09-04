from odoo.addons.website_sale_stock.tests.common import WebsiteSaleStockCommon
from odoo.fields import Command


class VariantPreselectCommon(WebsiteSaleStockCommon):
    """A storable, out-of-stock-blocking template with three variants in a known order.

    The attribute values carry an explicit sequence, so "first in configured order" is
    Red, then Green, then Blue -- independently of `product.product._order`, which sorts
    by `default_code, name, id` and is what core's grid and variant lookups walk.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.website.warehouse_id = cls.warehouse

        cls.attribute = cls.env["product.attribute"].create(
            {
                "name": "Test Color",
                "create_variant": "always",
                "value_ids": [
                    Command.create({"name": "Red", "sequence": 1}),
                    Command.create({"name": "Green", "sequence": 2}),
                    Command.create({"name": "Blue", "sequence": 3}),
                ],
            }
        )
        cls.red_value, cls.green_value, cls.blue_value = cls.attribute.value_ids

        # `_create_product` builds a `product.product`; we need the template so the
        # attribute line generates the three variants.
        cls.product = cls.env["product.template"].create(
            {
                "name": "Preselect test product",
                "type": "consu",
                "is_storable": True,
                "allow_out_of_stock_order": False,
                "list_price": 100.0,
                "uom_id": cls.uom_unit.id,
                "categ_id": cls.product_category.id,
                "website_published": True,
                "attribute_line_ids": [
                    Command.create(
                        {
                            "attribute_id": cls.attribute.id,
                            "value_ids": [Command.set(cls.attribute.value_ids.ids)],
                        }
                    ),
                ],
            }
        )
        assert len(cls.product.product_variant_ids) == 3, "setup must produce three variants"
        cls.red, cls.green, cls.blue = (
            cls._variant_for(cls.red_value),
            cls._variant_for(cls.green_value),
            cls._variant_for(cls.blue_value),
        )

    @classmethod
    def _variant_for(cls, attribute_value):
        return cls.product.product_variant_ids.filtered(
            lambda variant: attribute_value in variant.product_template_attribute_value_ids.product_attribute_value_id
        )
