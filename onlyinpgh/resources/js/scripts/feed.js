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

// Constructor should provide the following properties:
// - model: MapFeedItem object
// - clickCallback: a callback to pass a click event to (used to get event up to parent view)
// - template: template to render a model as a list item
var MapFeedItemView = Backbone.View.extend({
    tagName: 'li',

    markFocus: function(event) {
        this.$el.addClass('focused');
    },

    unmarkFocus: function(event) {
        this.$el.removeClass('focused');
    },

    // renders the feed item with the template provided in the constructor
    render: function() {
        console.log('rendering model ' + this.model.cid);
        this.$el.html(this.options.template(this.model.toJSON()));
        return this;
    }
});

// MapFeedView: Manages both the feed list and the map
// Constructor should provide the following:
// - model: MapFeedItems collection object
// - mapDOMElement: DOM element that a map should be attached to
// - mapOptions: a google.maps.MapOptions object (if center or zoom are left out
//               these components will be determined on first map draw by the
//               contents of the feed
// - itemTemplate: a template for rendering individual feed items
// - iwTemplate: an optional template for rendering an infoWindow
var MapFeedView = Backbone.View.extend({
    tagName: 'ul',
    map: null,
    subViews: {},   // map of feed item cids to {'marker': Marker, 'itemView': FeedItemView, 'infoWindow': InfoWindow} objects

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

    createSubView: function(model, itemTemplate, iwTemplate) {
        var itemView = new MapFeedItemView({
            model: model,
            template: itemTemplate
        });
        var marker = new google.maps.Marker({
            position: model.getLatLng(),
            icon: '/static/img/markers/place-marker.png'
        });
        var subView = {
            itemView: itemView,
            marker: marker,
            infoWindow: new google.maps.InfoWindow({
                content: iwTemplate(model.toJSON())
            })
        };

        var that = this;
        itemView.$el.click(function(event) {
            that.onItemFocus(subView);
        });
        google.maps.event.addListener(marker, 'click', function(event) {
            that.onItemFocus(subView);
        });
        return subView;
    },

    // callbacks for model/collection events
    onAdd: function(model, collection) {
        // create a FeedItemView and Marker bundle
        var subView = this.createSubView(model,
            this.options.itemTemplate,
            this.options.iwTemplate);
        this.subViews[model.cid] = subView;
        // render item view and append to own element
        this.$el.append(subView.itemView.render().el);
        // show the marker on the map
        subView.marker.setMap(this.map);
    },

    onReset: function(collection) {
        // remove all stored views
        for(var cid in this.subViews) {
            this.onRemove(this.subViews[cid].itemView.model);
        }
        this.subViews = {};

        // add new set of views
        for (var i = 0; i < collection.length; i++) {
            this.onAdd(collection.models[i], collection);
        }
        // don't need render: onAdd does it all
        // this.render();
    },

    onRemove: function(model, collection) {
        // all these deletes are necessary to remove the circular dependencies
        // between the subView and it's components' event callbacks
        var subView = this.subViews[model.cid];
        subView.infoWindow.close();
        delete subView.infoWindow;
        subView.itemView.remove();
        delete subView.itemView;
        subView.marker.setMap(null);
        delete subView.marker;
        delete this.subViews[model.cid];
    },

    onItemFocus: (function() {  // done as a closure to hide internal active iw state
        var focusedSubView = null;
        return function(subView) {
            if(focusedSubView && focusedSubView.infoWindow) {
                focusedSubView.infoWindow.close();
            }
            if(focusedSubView && focusedSubView.itemView) {
                focusedSubView.itemView.unmarkFocus();
            }
            subView.infoWindow.open(this.map, subView.marker);
            subView.itemView.markFocus();
            focusedSubView = subView;
        };
    }).call(this),

    render: function() {
        _.each(this.subViews, function(subView){
            this.$el.append(subView.itemView.render().el);
        }, this);
        return this;
    }
});