import { rpc } from "@web/core/network/rpc";
import { patch } from "@web/core/utils/patch";
import { CarouselProductCard } from "@website_sale/snippets/s_dynamic_snippet_products/carousel_product_card";

patch(CarouselProductCard.prototype, {
    /**
     * Open the product configurator on the first variant with stock.
     *
     * Core sends no combination, so the configurator starts on the first variant in
     * sequence even when it is sold out. Only template cards are concerned: a variant card
     * already carries its combination, and combos have their own configurator.
     */
    async onClickAddToCart(ev) {
        const dataset = ev.currentTarget.dataset;
        if (dataset.productSelected === "True" || dataset.productType === "combo") {
            return super.onClickAddToCart(ev);
        }
        const productTemplateId = parseInt(dataset.productTemplateId);
        const ptavs = await this.waitFor(
            rpc("/website_sale_stock_variant_preselect/first_available_combination", {
                product_template_id: productTemplateId,
            })
        );
        if (!ptavs.length) {
            return super.onClickAddToCart(ev);
        }

        await this.waitFor(
            this.services["cart"].add(
                {
                    productTemplateId: productTemplateId,
                    productId: parseInt(dataset.productId),
                    ptavs: ptavs,
                },
                {
                    showQuantity: Boolean(dataset.showQuantity),
                }
            )
        );
        if (this.add2cartRerender) {
            const dynamicSnippetProducts = this.el.closest(".s_dynamic_snippet_products");
            this.services["public.interactions"].stopInteractions(dynamicSnippetProducts);
            this.services["public.interactions"].startInteractions(dynamicSnippetProducts);
        }
    },
});
