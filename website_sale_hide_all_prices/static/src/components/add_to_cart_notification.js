/** @odoo-module **/

import { xml } from "@odoo/owl";
import { session } from "@web/session"
import {AddToCartNotification} from  "@website_sale/js/notification/add_to_cart_notification/add_to_cart_notification";
import {CartNotification} from  "@website_sale/js/notification/cart_notification/cart_notification";
import {WarningNotification} from  "@website_sale/js/notification/warning_notification/warning_notification";

class MyAddToCartNotification extends AddToCartNotification {
    setup(){
        super.setup();
        this.props['website_hide_all_prices'] = session['website_hide_all_prices']
    }
}

CartNotification.components = { AddToCartNotification: MyAddToCartNotification , WarningNotification  }

MyAddToCartNotification.template = 'website_hide_all_prices.MyAddToCartNotification'
