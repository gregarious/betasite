vloaders.offers_item = {
    init: function() {},
    render: function(element,data) {
        var postrender = function(html,data) {
            var back_link = $('<a href="#">Back</a>');
            back_link.click( function(event) {
                    load_view('offers_feed',element)
                    event.preventDefault();
                });
                
            element.html(back_link);
            element.append(html);
        }

        // simple: grab data and render single template
        $.getJSON(APP_SERVER+'/ajax/offer/'+data['id']+'?callback=?',
            function(json) {
                console.log(json);
                render_template('offers/item',json,postrender);
            });
    }
};