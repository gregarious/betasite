/*global Backbone, _, obid, define, require */

// all structure comes from API call
define(function(){
	// define models as separate at first to allow for inter-model references
	var PlacesFeedItem = Backbone.Model.extend();
	
	var PlacesFeed = Backbone.Collection.extend({
		model: PlacesFeedItem,
		url: obid.utils.to_api('places/app/feed'),
		// for debugging in the browser, use syncJSONP plugin
		sync: obid.settings.BROWSER_DEBUG ? Backbone.syncJSONP : Backbone.sync,
	});

	// return the models wrapped up in a module object
	return {
		PlacesFeedItem: PlacesFeedItem,
		PlacesFeed: PlacesFeed
	};
});
