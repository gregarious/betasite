// simple view: gets JSON for places from server and fills whole element with
// template for them
vloaders.places_feed = {
    init: function() {},
    render: function(element,data) {
        var postrender = function(html) {
            var home_link = $('<a id="home-link" href="#">Home</a>');
            home_link.click( function(event) {
                    load_view('home',element)
                    event.preventDefault();
                });
                
            element.html(home_link);
            element.append(html);
            
        }

        // simple: grab data and render single template
        $.getJSON('http://127.0.0.1:8000/ajax/places_feed?callback=?',
            function(json) {
                render_template('places/feed',json,postrender);
            });
    }
};