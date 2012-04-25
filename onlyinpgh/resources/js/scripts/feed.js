/* Requires jQuery, underscore, Backbone, google maps api */
var MapFeedItem = Backbone.Model.extend({
    // Returns a google.maps.LatLng object with this item's coordinates.
    // Default behavior is to get this from this object's latitude/longitude
    // properties, but this should be overwritten if necessary
    getLatLng: function() {
        return new google.maps.LatLng(
            this.attributes.location.latitude,
            this.attributes.location.longitude);
    }
});

var MapFeedItems = Backbone.Collection.extend({
    model: MapFeedItem
});

var MapFeedItemView = Backbone.View.extend({
    tagName: 'li',

    // the following should be set via extension
    template: null,
    iwTemplate: null,
    markerOptions: {},      // position will always be overwritten
    infoWindowOptions: {},  // content will always be overwritten

    marker: null,
    infoWindow: null,

    initialize: function(options) {
        console.log(this.model);
        this.marker = new google.maps.Marker(
            _.extend(_.clone(this.markerOptions), {
                position: this.model.getLatLng()
            })
        );
        this.infoWindow = new google.maps.InfoWindow(
            _.extend(_.clone(this.infoWindowOptions), {
                content: this.iwTemplate(this.model.toJSON())
            })
        );
    },

    markFocus: function(map) {
        this.$el.addClass('focused');
        this.infoWindow.open(map, this.marker);
    },

    unmarkFocus: function() {
        this.$el.removeClass('focused');
        this.infoWindow.close();
    },

    render: function(map) {
        console.log('rendering model ' + this.model.cid);
        this.$el.html(this.template(this.model.toJSON()));
        if(map) {
            this.marker.setMap(map);
        }
        return this;
    },

    close: function() {
        this.infoWindow.close();
        this.marker.setMap(null);
        this.remove();
    }
});

var MapFeedView = Backbone.View.extend({
    tagName: 'ul',
    map: null,
    SubViewClass: MapFeedItemView, // should be overridden to something concrete
    subViews: {},   // map of feed item cids to MapFeedItemViews

    initialize: function(options) {
        this.model.bind('reset', this.onReset, this);
        this.model.bind('add', this.onAdd, this);
        this.model.bind('remove', this.onRemove, this);
        this.initMap(options.mapDOMElement, options.mapOptions);
    },

    initMap: function(domElement, opts) {
        console.log('map init');
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
        google.maps.event.addListener(sv.marker, 'click', function(event) {
            that.onItemFocus(sv);
        });
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
