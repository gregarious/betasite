// simple view: gets JSON for events from server and fills whole element with
// template for them
vloaders.events_feed = {
    init: function() {},
    render: function(element,data) {
        // click handler for single event items
        var item_clicked = function(event) {
            load_view('events_single',element,{'id':event.data.eid});
            event.preventDefault();        
        }

        var postrender = function(html,data) {
            var home_link = $('<a id="home-link" href="#">Home</a>');
            home_link.click( function(event) {
                    load_view('home',element)
                    event.preventDefault();
                });
                
            element.html(home_link);
            element.append(html);

            for (var i = data.events.length - 1; i >= 0; i--) {
                var eid = data.events[i].id;
                element.find('#event-'+eid).click(
                    {'eid':eid},item_clicked);
            };
        }

        // simple: grab data and render single template
        $.getJSON('http://127.0.0.1:8000/ajax/events_feed?callback=?',
            function(json) {
                render_template('events/feed',json,postrender);
            });
    }
};