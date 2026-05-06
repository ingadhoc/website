/** @odoo-module **/
/**
 * GA4 User Tracking
 *
 * Tracks authentication events on the login/signup page:
 *   sign_up  – user submits the registration form
 *   login    – user submits the login form
 */

import { registry } from '@web/core/registry';
import { Interaction } from '@web/public/interaction';

export class GA4UserTracking extends Interaction {
    static selector = '.oe_website_login_container';

    dynamicContent = {
        'button.ga4_on_user_signup': {
            't-on-click': this.onUserSignup,
        },
        '.oe_login_form button[type="submit"]': {
            't-on-click': this.onUserLogin,
        },
    };

    _trackGa4(name, params) {
        const ga = window.gtag;
        if (typeof ga === 'function') {
            ga('event', name, params);
            // eslint-disable-next-line no-console
            console.debug('[GA4]', name, params);
        }
    }

    onUserSignup() {
        this._trackGa4('sign_up', { method: 'email' });
    }

    onUserLogin() {
        this._trackGa4('login', { method: 'email' });
    }
}

registry
    .category('public.interactions')
    .add('ga4_ecommerce.GA4UserTracking', GA4UserTracking);
