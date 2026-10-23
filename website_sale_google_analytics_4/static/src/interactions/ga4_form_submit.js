/** @odoo-module **/
/**
 * GA4 form_submit.
 *
 * The one event of a website form that GA4 cannot measure on its own.
 * Enhanced measurement listens for the browser `submit` event, and the Odoo
 * form snippet never fires it: the button is an anchor handled by a click,
 * and the form is sent over JS.
 *
 * `search` and `form_start`, which came from the same place as this one, are
 * NOT re-implemented here: enhanced measurement already covers them --
 * `view_search_results` for the `search` URL parameter, which Odoo uses, and
 * `form_start` under that very name.
 */

import { patch } from '@web/core/utils/patch';
import { Form } from '@website/snippets/s_website_form/form';

patch(Form.prototype, {
    async send() {
        // Before the call, not after: a form configured to redirect on success
        // navigates away, and the event would never leave the page.
        const ga = window.gtag;
        if (typeof ga === 'function') {
            ga('event', 'form_submit', {
                form_id: this.el.id || '',
                form_destination: this.el.dataset.model_name || '',
            });
        }
        return super.send(...arguments);
    },
});
