vloaders.home = {
    init: function() {},
    render: function(element,data) {
        // helper function that binds view loaders to the current element
        var bind_navclick = function(link,vloader,data) {
            link.click( function(event) {
                load_view(vloader,element,data)
                event.preventDefault();
            });
        }
        
        var to_hotlist = function(html) {
            element.find('#content').html(html);

            
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

            $.getJSON(APP_SERVER+'/ajax/hot_feed?callback=?',
                function(json) {
                    render_template('hot',json,to_hotlist);
                });

            render_template('main_nav',{},to_mainnav);
        }

        render_template('feed_container',{},to_feedcontainer);
    }
};