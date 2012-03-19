// Main entrypoint for all JS

/*global $, Mustache, Backbone, _, obid, require */
/*jshint browser:true */
/*jshint devel:true */

// ready script
$(function() {
    'use strict';
    console.log('BROWSER_DEBUG: ' + obid.settings.BROWSER_DEBUG);

    // we get a promise that will be resolved when the routers are set up
    var configuringApp = configApp();
    
    $(document).on('deviceready',function(){  // ensure phonegap API is hooked up to device
        $.ajaxSetup({
            timeout: 5000
        });
        console.log('BROWSER_DEBUG: ' + obid.settings.BROWSER_DEBUG);
        console.log('AJAX global timeout set to 5s.');

        // device is ready, so once routers are ready, let's go!
        configuringApp.done(function(){
            console.log('starting app');
            Backbone.history.start();
        });
        console.log('Using API_URL: '+obid.settings.API_URL);
    });

    // if we're debugging in the browser, manually call this
    if(obid.settings.BROWSER_DEBUG) {
        $(document).trigger('deviceready');
    }

    function configApp() {
        // since we use require below, we become asynchronous.
        // we need to return a promise for when we're done.
        var configuringApp = $.Deferred();
        
        // TODO: make this more selective script loading. For now just load it all up front.
        require(
            ["models/places",
             "views/places_feed",
             "views/place_detail",
             "views/nav_header"],
            function(models,feed_views,detail_views,header_views) {

            // TODO: move these functions into some backbone plugin/util places
            // Function will fill the html of the given selector with the view content
            var showView = function(selector,view) {
                // TODO: save view connected to each selector
                $(selector).html(view.render().el);
                return view;
            };

            // Function will fetch all data necessary to fill given model, create
            //  a view with the model, and render that view to the given selector.
            //
            // Arguments:
            //  * view_func: a function that takes in a model/collection and outputs
            //      a Backbone.View instance
            var fetchAndShow = function(selector,model,view_func,spinner) {
                if(spinner) {
                    $(selector).html('<div class="spinner">Loading...</div>');
                }
                model.fetch({
                    // callback could return model or collection as first arg
                    success: function(model,response) {
                        // TODO: should we be doing a call() here?
                        showView(selector, view_func(model));
                    },
                    error: function(model,response) {
                        $(selector).html('<p>error: ' + response.statusText+'</p>');
                    }
                });
            };

            var AppRouter = Backbone.Router.extend({
                routes: {
                    '':'home',
                    'places':'places_feed',
                    'places/:id':'place_detail',
                    'events':'events_feed',
                    'events/:id':'event_detail',
                    'specials':'specials_feed',
                    'specials/:id':'specials_detail'
                },

                initialize: function(){
                    showView('header',new header_views.NavHeader());
                },

                home: function(){
                    // no-op for now
                },

                places_feed: function(){
                    var feed = new models.PlacesFeed();
                    fetchAndShow('#container', feed, function(collection) {
                        return new feed_views.PlacesFeedView({model: collection});
                    }, true);
                },

                place_detail: function(id){
                    var place = new models.PlaceDetail({id:id});
                    fetchAndShow('#container', place, function(model) {
                        return new detail_views.PlaceDetailView({model: model});
                    }, true);
                },

                events_feed: function() {
                    $("#container").html('events feed!');
                },

                event_detail: function(id) {
                    $("#container").html('event ' + id + ' detail!');
                },

                specials_feed: function() {
                    $("#container").html('specials feed!');
                },

                special_detail: function(id) {
                    $("#container").html('special' + id + ' detail!');
                }
            });
            
            // creating the new Router registers it with Backbone
            window.app = new AppRouter();

            configuringApp.resolve();
        });
        return configuringApp.promise();
    }
});

