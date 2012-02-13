vloaders.home = {
    init: function() {},
    render: function(element,data) {
        // helper function that binds view loaders to the current element
        var click_bind = function(link,vloader,data) {
            link.click( function(event) {
                load_view(vloader,element,data)
                event.preventDefault();
            });
        }
        
        var postrender = function(html) {
            element.html(html);
            click_bind($('#events-link'),'events_feed');
            click_bind($('#places-link'),'places_feed');
            click_bind($('#specials-link'),'specials_feed');
        }

        render_template('home',{},postrender);
    }
};