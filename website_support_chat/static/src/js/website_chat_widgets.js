function get_open_webite_chat() {

    openerp.jsonRpc('/website_support_chat/get_values', 'call', {
            }).then(function (values) {
                id = values['id'];
                login = values['login'];
                tag = values['tag'];
                img = values['img'];
                bubble = values['bubble'];
                if(login == "public"){
                (function(t,a,l,k,u,s,_){if(!t[u]){t[u]=function(){(t[u].q=t[u].q||[]).push(arguments)},t[u].l=1*new Date();s=a.createElement(l),_=a.getElementsByTagName(l)[0];s.async=1;s.src=k;_.parentNode.insertBefore(s,_)}})(window,document,'script','//www.talkus.io/plugin.js','talkus');
                talkus('create', id);
                talkus('loadingImage', img);
                talkus('tag', tag);
                talkus('bubble', bubble);

                }

            });

}

get_open_webite_chat();

