/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.FacebookPixelTrackingUser = publicWidget.Widget.extend({
    selector: '.oe_website_login_container',
    events: {
        "click button.on_user_signup": "_onUserSignup",
    },

    _pushInfo: function (event, dict){
        if(typeof(fbq) !== 'undefined'){
            fbq('track', event, dict);
            console.log(dict);
        }
    },
    _onUserSignup: function () {
        const user_email = $("#login").val();
        const dict = {
            'user_email':user_email,
        }
        this._pushInfo('user_signup', dict);
    },
});
