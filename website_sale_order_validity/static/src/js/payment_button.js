/** @odoo-module **/

import paymentButton from '@payment/js/payment_button';

paymentButton.include({
    async start() {
        await this._super(...arguments);
        const updateCartButton = document.getElementById('update_cart_button');
        if (updateCartButton) {
            this.paymentButton.addEventListener('click', this.stopEventPropagation, true);
        }
    },

    stopEventPropagation(event) {
        event.preventDefault();
        event.stopPropagation();
    },
});
