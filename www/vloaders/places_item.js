vloaders.places_item = {
    init: function() {},
    render: function(element,data) {
        var postrender = function(html,data) {
            var back_link = $('<a href="#">Back</a>');
            back_link.click( function(event) {
                    load_view('places_feed',element)
                    event.preventDefault();
                });
                
            element.html(back_link);
            element.append(html);
        }

        // simple: grab data and render single template
        $.getJSON('http://127.0.0.1:8000/ajax/place/'+data['id']+'?callback=?',
            function(json) {
                console.log(json);
                render_template('places/item',json,postrender);
            });
    }
};