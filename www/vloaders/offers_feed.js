// simple view: gets JSON for offers from server and fills whole element with
// template for them
vloaders.offers_feed = {
    init: function() {},
    render: function(element,data) {
        // helper function that binds view loaders to the current element
        var bind_navclick = function(link,vloader) {
            link.click( function(event) {
                load_view(vloader,element)
                event.preventDefault();
            });
        }

        // click handler for single event items
        var item_clicked = function(event) {
            load_view('offers_item',element,{'id':event.data.id});
            event.preventDefault();        
        }

        var to_speciallist = function(html,data) {
            element.find('#content').html(html);

            for (var i = data.specials.length - 1; i >= 0; i--) {
                var pid = data.specials[i].id;
                element.find('#special-item-'+pid).click(
                    {'id':pid},item_clicked);
            };
        }

        var to_mainnav = function(html) {
            element.find('#main-nav').html(html);
            bind_navclick($('#navlink-hot'),'home');
            bind_navclick($('#navlink-places'),'places_feed');
            bind_navclick($('#navlink-events'),'events_feed');
            bind_navclick($('#navlink-specials'),'offers_feed');
            // bind_navclick($('#navlink-chatter'),'chatter_feed');
            // bind_navclick($('#navlink-news'),'news_feed');
            // bind_navclick($('#navlink-jobs'),'jobs_feed');
        }

        var to_feedcontainer = function(html) {
            element.html(html); // fills container

            $.getJSON(APP_SERVER+'/ajax/offers_feed?callback=?',
                function(json) {
                    render_template('offers/feed',json,to_speciallist);
                });

            render_template('main_nav',{},to_mainnav);
        }

        render_template('feed_container',{},to_feedcontainer);
    }
};