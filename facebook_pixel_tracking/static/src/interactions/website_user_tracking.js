/** @odoo-module **/
import { registry } from '@web/core/registry';
import { Interaction } from '@web/public/interaction';

export class FacebookPixelTrackingUser extends Interaction {
    static selector = '.oe_website_login_container';

    dynamicContent = {
        'form.oe_signup_form button[type="submit"]': { 't-on-click': this.onUserSignup },
    };

    _pushInfo(event, dict) {
        if (typeof fbq !== 'undefined') {
            fbq('track', event, dict);
        }
    }

    onUserSignup() {
        this._pushInfo('user_signup', {
            user_email: this.el.querySelector('form.oe_signup_form #login')?.value,
        });
    }
}

registry
    .category('public.interactions')
    .add('facebook_pixel_tracking.FacebookPixelTrackingUser', FacebookPixelTrackingUser);
