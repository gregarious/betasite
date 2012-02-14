// simple view: gets JSON for events from server and fills whole element with
// template for them

vloaders.events_feed = {
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
            load_view('events_item',element,{'id':event.data.id});
            event.preventDefault();        
        }


        var to_eventlist = function(html,data) {
            element.find('#content').html(html);

            for (var i = data.events.length - 1; i >= 0; i--) {
                var eid = data.events[i].id;
                element.find('#event-item-'+eid).click(
                    {'id':eid},item_clicked);
            };
        }

        var to_mainnav = function(html) {
            element.find('#main-nav').html(html);
            bind_navclick($('#navlink-hot'),'home');
            bind_navclick($('#navlink-places'),'places_feed');
            bind_navclick($('#navlink-events'),'events_feed');
            bind_navclick($('#navlink-specials'),'specials_feed');
            // bind_navclick($('#navlink-chatter'),'chatter_feed');
            // bind_navclick($('#navlink-news'),'news_feed');
            // bind_navclick($('#navlink-jobs'),'jobs_feed');
        }

        var to_feedcontainer = function(html) {
            element.html(html); // fills container

            $.getJSON('http://127.0.0.1:8000/ajax/events_feed?callback=?',
                function(json) {
                    render_template('events/feed',json,to_eventlist);
                });

            render_template('main_nav',{},to_mainnav);
        }

        render_template('feed_container',{},to_feedcontainer);
    }
};
