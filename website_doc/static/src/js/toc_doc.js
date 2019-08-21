odoo.define('webside_doc.webside_doc', function (require) {
'use strict';

require('web.dom_ready');
var ajax = require('web.ajax');
var config = require('web.config');
var Widget = require('web.Widget');

if(!$('.o_website_doc').length) {
    return $.Deferred().reject("DOM doesn't contain '.o_website_doc'");
}

    // Nav Menu ScrollSpy
    var NavigationSpyMenu = Widget.extend({
        start: function(watched_selector){
            this.authorized_text_tag = ['em', 'b', 'i', 'u'];
            this.spy_watched = $(watched_selector);
            this.generateMenu();
        },
        generateMenu: function(){
            var self = this;
            // reset ids
            $("[id^=doc_header_], [id^=doc_]", this.spy_watched).attr("id", "");
            // generate the new spy menu
            var last_li = false;
            var last_ul = null;
            _.each(this.spy_watched.find("h1, h2, h3"), function(el){
                var id, text;
                switch (el.tagName.toLowerCase()) {
                    case "h1":
                        id = self.setElementId('doc_header_', el);
                        text = self.extractText($(el));
                        if (!text) {
                            break;
                        }
                        last_li = $("<li>").append($('<a href="#'+id+'"/>').text(text)).appendTo(self.$el);
                        last_ul = false;
                        break;
                    case "h2":
                        id = self.setElementId('doc_', el);
                        text = self.extractText($(el));
                        if (!text) {
                            break;
                        }
                        if (last_li) {
                            if (!last_ul) {
                                last_ul = $("<ul class='nav'>").appendTo(last_li);
                            }
                            $("<li>").append($('<a href="#'+id+'"/>').text(text)).appendTo(last_ul);
                        }
                        break;
                }
            });
        },
        setElementId: function(prefix, $el){
            var id = _.uniqueId(prefix);
            this.spy_watched.find($el).attr('id', id);
            return id;
        },
        extractText: function($node){
            var self = this;
            var raw_text = [];
            _.each($node.contents(), function(el){
                var current = $(el);
                if($.trim(current.text())){
                    var tagName = current.prop("tagName");
                    if(_.isUndefined(tagName) || (!_.isUndefined(tagName) && _.contains(self.authorized_text_tag, tagName.toLowerCase()))){
                        raw_text.push($.trim(current.text()));
                    }
                }
            });
            return raw_text.join(' ');
        }
    });

    var nav_menu = new NavigationSpyMenu();
    nav_menu.setElement($('[data-id="doc_sidebar"]'));
    nav_menu.start($('body[data-target=".navspy"]'));

    var $bs_sidebar = $(".o_website_doc .bs-sidebar");
    $(window).on('resize', _.throttle(adapt_sidebar_position, 200, {leading: false}));
    adapt_sidebar_position();

    function adapt_sidebar_position() {
        $bs_sidebar.css({
            position: "",
            width: "",
        });
        if (config.device.size_class >= config.device.SIZES.MD) {
            $bs_sidebar.css({
                position: "fixed",
                width: $bs_sidebar.outerWidth(),
            });
        }
    }

    $bs_sidebar.affix({
        offset: {
            top: 0,
            bottom: $('body').height() - $('#wrapwrap').outerHeight() + $("footer").outerHeight(),
        },
    });
});
