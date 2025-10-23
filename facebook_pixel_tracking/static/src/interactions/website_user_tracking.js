/** @odoo-module **/
import { registry } from '@web/core/registry';
import { Interaction } from '@web/public/interaction';

export class FacebookPixelTrackingUser extends Interaction {
    static selector = ".oe_website_login_container";

    dynamicContent = {
        'button.on_user_signup': { 't-on-click': this.onUserSignup },
    };

    _pushInfo(event, dict) {
        if(typeof(fbq) !== 'undefined'){
            fbq('track', event, dict);
            console.log(dict);
        }
    }

    onUserSignup() {
        const user_email = document.getElementById("login").value;
        const dict = {
            'user_email':user_email,
        }
        this._pushInfo('user_signup', dict);
    }
}

registry.category('public.interactions').add('facebook_pixel_tracking.FacebookPixelTrackingUser', FacebookPixelTrackingUser);
