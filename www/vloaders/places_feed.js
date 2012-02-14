// simple view: gets JSON for places from server and fills whole element with
// template for them
vloaders.places_feed = {
    init: function() {},
    render: function(element,data) {
        // helper function that binds view loaders to the current element
        var click_bind = function(link,vloader,data) {
            link.click( function(event) {
                load_view(vloader,element,data)
                event.preventDefault();
            });
        }

        var to_placelist = function(html) {
            element.find('#content').html(html);
        }

        var to_mainnav = function(html) {
            element.find('#main-nav').html(html);
            click_bind($('#navlink-hot'),'home');
            click_bind($('#navlink-places'),'places_feed');
            click_bind($('#navlink-events'),'events_feed');
            click_bind($('#navlink-specials'),'specials_feed');
            // click_bind($('#navlink-chatter'),'chatter_feed');
            // click_bind($('#navlink-news'),'news_feed');
            // click_bind($('#navlink-jobs'),'jobs_feed');
        }

        var to_feedcontainer = function(html) {
            element.html(html); // fills container

            $.getJSON('http://127.0.0.1:8000/ajax/places_feed?callback=?',
                function(json) {
                    render_template('places/feed',json,to_placelist);
                });

            render_template('main_nav',{},to_mainnav);
        }

        render_template('feed_container',{},to_feedcontainer);
    }
};