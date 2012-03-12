/*global Backbone, _, obid, define, require */
/*jshint browser:true */
/*jshint devel:true */

define(function(){
	'use strict';
	// all structure comes from API call
	return {
		PlacesFeedItem: Backbone.Model.extend(),
	
		PlacesFeed: Backbone.Collection.extend({
			model: this.PlacesFeedItem,
			url: obid.utils.to_api('places/app/feed'),
			// for debugging in the browser, use syncJSONP plugin
			sync: obid.settings.BROWSER_DEBUG ? Backbone.syncJSONP : Backbone.sync
		})
	};
});
