/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.searchBar.include({


    _pushInfo: function (dict){
        if(typeof(dataLayer) !== 'undefined'){
            dataLayer.push(dict);
            console.log(dict);
        }
    },

    /**
     * @override
     */
    _onSearch: function (ev) {
        const search_term = ev.target.value
        const dict = {
            'event': 'search',
            'ecommerce': {
                'search_term': search_term
            }
        }
        this._pushInfo(dict)
        this._super(...arguments);
    },
});

publicWidget.registry.s_website_form.include({
    _pushInfo: function (dict){
        if(typeof(dataLayer) !== 'undefined'){
            dataLayer.push(dict);
            console.log(dict);
        }
    },
    /**
     * @override
     */
    send: async function (e) {
        const dataTarget = e.target.closest("form")
            const form_name = dataTarget.id;
            const form_destination = dataTarget.dataset.model_name
            const dict = {
                'event': 'form_submit',
                'ecommerce': {
                    'form_name': form_name,
                    'form_destination': form_destination
                }
            }
            this._pushInfo(dict)
            this._super(...arguments);
    }
})
