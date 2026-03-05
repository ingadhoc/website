/** @odoo-module **/
import { registry } from '@web/core/registry';
import { Interaction } from '@web/public/interaction';

export class GoogleTagManagerAdvancedTrackingUser extends Interaction {
    static selector = ".oe_website_login_container";

    dynamicContent = {
        'button.on_user_signup': { 't-on-click': this.onUserSignup },
    };

    _pushInfo(dict){
        if (typeof (dataLayer) !== 'undefined') {
            dataLayer.push(dict);
            console.log(dict);
        }
    }
    onUserSignup() {
        const user_email = document.getElementById("login").value;
        const dict = {
            'event':'user_signup',
            'user_email':user_email,
        }
        this._pushInfo(dict);
    }
}

registry.category('public.interactions').add('google_tag_manager_advanced_tracking.GoogleTagManagerAdvancedTrackingUser', GoogleTagManagerAdvancedTrackingUser);
