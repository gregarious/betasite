/* Requires jQuery, underscore, Backbone, google maps api */
scenable = window.scenable = window.scenable || {};

scenable.mapFeed = (function(){
    var Item = Backbone.Model.extend({
        // Returns a google.maps.LatLng object with this item's coordinates, or null
        // Default behavior is to get this from this object's latitude/longitude
        // properties, but this should be overwritten if necessary
        getLatLng: function() {
            var loc = this.attributes.location;
            if(loc &&
               loc.latitude !== null && !_.isUndefined(loc.latitude) &&
               loc.longitude !== null && !_.isUndefined(loc.longitude)) {
                return new google.maps.LatLng(loc.latitude, loc.longitude);
            }
            else {
                return null;
            }
        }
    });

    var ItemFeed = Backbone.Collection.extend({
        model: Item
    });

    var ItemView = Backbone.View.extend({
        tagName: 'li',

        // the following should be set via extension
        template: null,
        iwTemplate: null,
        markerOptions: {},      // position will always be overwritten
        InfoWindowOptions: {       // content will always be overwritten
            maxWidth: 300
            // closeBoxURL: "http://www.google.com/intl/en_us/mapfiles/close.gif",
            // InfoWindowClearance: new google.maps.Size(1, 100),
            // isHidden: false,
            // pane: "floatPane",
            // enableEventPropagation: false,
            // alignBottom: true,
            // pixelOffset: new google.maps.Size(0, -40)
        },

        marker: null,
        InfoWindow: null,

        initialize: function(options) {
            var position = this.model.getLatLng();
            if(position !== null){
                this.marker = new google.maps.Marker(
                    _.extend(_.clone(this.markerOptions), {position: position})
                );
            }
            this.InfoWindow = new google.maps.InfoWindow(
                _.extend(_.clone(this.InfoWindowOptions), {
                    content: this.iwTemplate(this.model.toJSON())
                })
            );
        },

        markFocus: function(map) {
            this.$el.addClass('focused');
            if(this.InfoWindow && this.marker) {
                this.InfoWindow.open(map, this.marker);
            }
        },

        unmarkFocus: function() {
            this.$el.removeClass('focused');
            if(this.InfoWindow) {
                this.InfoWindow.close();
            }
        },

        render: function(map) {
            this.$el.html(this.template(this.model.toJSON()));
            if(map && this.marker) {
                this.marker.setMap(map);
            }
            return this;
        },

        close: function() {
            if(this.InfoWindow) {
                this.InfoWindow.close();
            }
            if(this.marker) {
                this.marker.setMap(null);
            }
            this.remove();
        }
    });

    var FeedView = Backbone.View.extend({
        tagName: 'ul',
        map: null,
        SubViewClass: ItemView, // should be overridden to something concrete
        subViews: {},   // map of feed item cids to MapFeedItemViews

        initialize: function(options) {
            this.model.bind('reset', this.onReset, this);
            this.model.bind('add', this.onAdd, this);
            this.model.bind('remove', this.onRemove, this);
            this.map = scenable.map.mapFactory('feed',
                options.mapDOMElement, options.mapOptions);
        },

        initMap: function(domElement, opts) {
            this.map = new google.maps.Map(domElement, opts);
        },

        createSubView: function(model) {
            var sv = new this.SubViewClass({
                model: model
            });
            var that = this;
            sv.$el.click(function(event) {
                that.onItemFocus(sv);
            });
            if(sv.marker) {
                google.maps.event.addListener(sv.marker, 'click', function(event) {
                    that.onItemFocus(sv);
                });
            }
            return sv;
        },

        // callbacks for model/collection events
        onAdd: function(model, collection) {
            // create a FeedItemView and Marker bundle
            var subView = this.createSubView(model);
            this.subViews[model.cid] = subView;
            // render item view and append to own element
            this.$el.append(subView.render(this.map).el);
        },

        onReset: function(collection) {
            // remove all stored views
            _.each(this.subViews, function(sv) {
                sv.close();
            });
            this.subViews = {};

            // add new set of views
            _.each(collection.models, function(model) {
                this.subViews[model.cid] = this.createSubView(model);
            }, this);
            this.render();
        },

        onRemove: function(model, collection) {
            this.subViews[model.cid].close();
            delete this.subViews[model.cid];
        },

        onItemFocus: (function() {  // done as a closure to hide internal focused state
            var focusedSubView = null;
            return function(subView) {
                if(focusedSubView) {
                    focusedSubView.unmarkFocus();
                }
                subView.markFocus(this.map);
                focusedSubView = subView;
            };
        }).call(this),

        render: function() {
            _.each(this.subViews, function(subView){
                this.$el.append(subView.render(this.map).el);
            }, this);
            return this;
        }
    });

    // actual export of variables
    return {
        Item: Item,
        ItemFeed: ItemFeed,
        ItemView: ItemView,
        FeedView: FeedView
    };
})();