function get_open_webite_chat() {
    openerp.jsonRpc('/website_talkus/get_values', 'call', {
            }).then(function (values) {
                id = values['id'];
                login = values['login'];
                tag = values['tag'];
                // img = values['img'];
                // backgroud_color = values['backgroud_color'];
                // border_color = values['border_color'];
                bubble = values['bubble'];
                // welcomeMessage = values['welcomeMessage'];
               if(login == "public"){
                    (function(t,a,l,k,u,s,e){if(!t[u]){t[u]=function(){(t[u].q=t[u].q||[]).push(arguments)},t[u].l=1*new Date();s=a.createElement(l),e=a.getElementsByTagName(l)[0];s.async=1;s.src=k;e.parentNode.insertBefore(s,e)}})(window,document,'script','//www.talkus.io/plugin.beta.js','talkus');
                    // (function(t,a,l,k,u,s,_){if(!t[u]){t[u]=function(){(t[u].q=t[u].q||[]).push(arguments)},t[u].l=1*new Date();s=a.createElement(l),_=a.getElementsByTagName(l)[0];s.async=1;s.src=k;_.parentNode.insertBefore(s,_)}})(window,document,'script','//www.talkus.io/plugin.js','talkus');
                    talkus('init', id, { tag: 'comercial'});
                    // DEPRECEATED
                    // talkus('create', id);
                    // talkus('loadingImage', img);
                    talkus('bubble', bubble);
                    // talkus('welcomeMessage', welcomeMessage);
                    // talkus('identify', { tag: 'comercial'});
                    // if(backgroud_color && border_color)
                    //     talkus('primaryColor', backgroud_color, border_color);
               }
            });

}

get_open_webite_chat();
