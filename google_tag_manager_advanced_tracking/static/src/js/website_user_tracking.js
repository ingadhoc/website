/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.GoogleTagManagerUserAdvancedTracking = publicWidget.Widget.extend({
    selector: '.oe_website_login_container',
    events: {
        "click button.on_user_signup": "_onUserSignup",
    },
    _pushInfo: function (dict){
        if(typeof(dataLayer) !== 'undefined'){
            dataLayer.push(dict);
            console.log(dict);
        }
    },
    _onUserSignup: function () {
        const user_email = $("#login").val()
        const dict = {
            'event':'user_signup',
            'user_email':user_email,
        }
        this._pushInfo(dict);
    },
});
