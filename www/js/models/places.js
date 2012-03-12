/*global Backbone, _, obid, define, require */
/*jshint browser:true */
/*jshint devel:true */

define(function(){
	'use strict';
	// all structure comes from API call
	var PlacesFeedItem = Backbone.Model.extend();
	
	var PlacesFeed = Backbone.Collection.extend({
		model: PlacesFeedItem,
		url: obid.utils.to_api('places/app/feed'),
		// for debugging in the browser, use syncJSONP plugin
		sync: obid.settings.BROWSER_DEBUG ? Backbone.syncJSONP : Backbone.sync
	});

	// return the models wrapped up in a module object
	return {
		PlacesFeedItem: PlacesFeedItem,
		PlacesFeed: PlacesFeed
	};
});
