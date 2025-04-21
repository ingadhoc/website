/** @odoo-module **/

import {AddToCartNotification} from  "@website_sale/js/notification/add_to_cart_notification/add_to_cart_notification";
import {CartNotification} from  "@website_sale/js/notification/cart_notification/cart_notification";
import {WarningNotification} from  "@website_sale/js/notification/warning_notification/warning_notification";

class TrackingAddToCartNotification extends AddToCartNotification {
    setup(){
        super.setup();
    }
}

CartNotification.components = { AddToCartNotification: TrackingAddToCartNotification , WarningNotification  }

AddToCartNotification.template = 'website_sale_advanced_tracking.TrackingAddToCartNotification'
