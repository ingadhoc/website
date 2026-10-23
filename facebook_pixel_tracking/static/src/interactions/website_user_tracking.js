/** @odoo-module **/
import { registry } from '@web/core/registry';
import { Interaction } from '@web/public/interaction';

export class FacebookPixelTrackingUser extends Interaction {
    static selector = '.oe_website_login_container';

    dynamicContent = {
        'form.oe_signup_form button[type="submit"]': { 't-on-click': this.onUserSignup },
    };

    onUserSignup() {
        // trackCustom, not track: user_signup is not one of Meta's standard
        // events, and track silently drops what it does not know. The email
        // no longer travels with it -- it went in clear text, and the partner
        // already reaches Meta hashed through the Conversions API.
        if (typeof fbq !== 'undefined') {
            fbq('trackCustom', 'user_signup');
        }
    }
}

registry
    .category('public.interactions')
    .add('facebook_pixel_tracking.FacebookPixelTrackingUser', FacebookPixelTrackingUser);
