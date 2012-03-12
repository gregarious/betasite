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
        var app;    // initialized to AppRouter below
        // TODO: make this more selective script loading. For now just load it all up front.
        require(
            ["models/places",
             "views/places_feed",
             "views/place_detail"],
            function(models,feed_views,detail_views) {

            var AppRouter = Backbone.Router.extend({
                routes: {
                    '':'home',
                    'places':'places_feed',
                    'places/:id':'place_detail'
                },

                home: function(){
                    console.log('Router: home');
                    // Temporary redirect
                    this.navigate('places', true);
                },

                places_feed: function(){
                    console.log('Router: places_feed');
                    var feed = new models.PlacesFeed();
                    console.log('spinner on');
                    feed.fetch({
                        success: function(collection,response) {
                            console.log('spinner off');
                            app.showView('#container',
                                new feed_views.PlacesFeedView({model:collection}));
                        },
                        error: function(collection,response) {
                            console.log('error! ' + response.statusText);
                            console.log('spinner off');
                        }
                    });
                },

                place_detail: function(id){
                    console.log('Router: place_detail');
                    var place = new models.PlaceDetail({id:id});

                    console.log('spinner on');
                    place.fetch({
                        success: function(model,response) {
                            console.log('spinner off');
                            app.showView('#container',
                                new detail_views.PlaceDetailView({model:model}));
                        },
                        error: function(model,response) {
                            console.log('error! ' + response.statusText);
                            console.log('spinner off');
                        }
                    });
                },

                showView: function(selector, view) {
                    this.currentView = view;
                    $(selector).html(this.currentView.render().el);
                    return view;
                }
            });
            
            // creating the new Router registers it with Backbone
            app = new AppRouter();

            configuringApp.resolve();
        });
        return configuringApp.promise();
    }
});

