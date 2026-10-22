/** @odoo-module **/
/**
 * GA4 site events: the ones Odoo does not fire by itself.
 *
 *   search      – a results page was opened with a search term
 *   form_start  – the visitor reached a website form for the first time
 *   form_submit – the visitor submitted it
 *
 * They used to live in google_tag_manager_advanced_tracking, pushed to the
 * dataLayer; here they go straight to gtag, like the rest of this module.
 */

import { registry } from '@web/core/registry';
import { patch } from '@web/core/utils/patch';
import { Interaction } from '@web/public/interaction';
import { Form } from '@website/snippets/s_website_form/form';

function _trackGa4(name, params) {
    const ga = window.gtag;
    if (typeof ga === 'function') {
        ga('event', name, params);
    }
}

function _formParams(formEl) {
    return {
        form_id: formEl.id || '',
        form_destination: formEl.dataset.model_name || '',
    };
}

export class GA4SiteEvents extends Interaction {
    static selector = '#wrapwrap';

    dynamicContent = {
        // .once: one form_start per form per page load, no bookkeeping needed.
        '.s_website_form_rows': { 't-on-focusin.once': this.onFormStart },
    };

    start() {
        // Reported from the results page rather than from the search box, so
        // that every way in counts: the shop filters, the suggestion list and
        // a pasted link alike.
        const term = new URLSearchParams(window.location.search).get('search');
        if (term) {
            _trackGa4('search', { search_term: term });
        }
    }

    onFormStart(ev) {
        const formEl = ev.target.closest('form');
        if (formEl) {
            _trackGa4('form_start', _formParams(formEl));
        }
    }
}

registry
    .category('public.interactions')
    .add('website_sale_google_analytics_4.GA4SiteEvents', GA4SiteEvents);

patch(Form.prototype, {
    async send() {
        // Before the call, not after: a form configured to redirect on success
        // navigates away, and the event would never leave the page.
        _trackGa4('form_submit', _formParams(this.el));
        return super.send(...arguments);
    },
});
