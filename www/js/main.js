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
        require(["models/places","views/places_feed","views/place_detail"],function(models,feed_views,detail_views) {

            var AppRouter = Backbone.Router.extend({
                routes: {
                    '':'home',
                    'places':'places_feed'
                    //'places/:id/':'place_detail'
                },

                home: function(){
                    //alert('home');
                    this.navigate('/places', true);
                },

                places_feed: function(){
                    //alert('feed');
                    this.feed = new models.PlacesFeed();
                    this.feedView = new feed_views.PlacesFeedView({model:this.feed});
                    console.log('spinner on');
                    // This call is asynchronous. Will reset the collection when it returns, which
                    //  will DYNAMICALLY insert items into the rendered HTMLElement (feedView.el).
                    this.feed.fetch({
                        success: function(collection,response) { console.log('success! ' + collection.length + ' objects fetched.'); console.log('spinner off'); },
                        error: function(collection,response) { console.log('error! ' + response.statusText); console.log('spinner off'); }
                    });

                    // THIS "el" CONTENT IS NOT STATIC! See note above
                    $('#container').html(this.feedView.render().el);
                },

                place_detail: function(id){
                    //alert('detail');
                    this.place = new this.PlacesDetail({id:id});
                    this.detailView = new detail_views.PlaceDetailView();

                    console.log('spinner on');
                    this.place.fetch({
                        success: function(collection,response) { console.log('success!'); console.log('spinner off'); },
                        error: function(collection,response) { console.log('error! ' + response.statusText); console.log('spinner off'); }
                    });

                    $('#container').html(this.detailView.render().el);
                }
            });
            
            // creating the new Router registers it with Backbone
            var app = new AppRouter();

            configuringApp.resolve();
        });
        return configuringApp.promise();
    }
});
