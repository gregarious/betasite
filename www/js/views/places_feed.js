/*global Backbone, _, $, Mustache, require, define */
/*jshint browser:true */
/*jshint devel:true */

define(['text!../../templates/places/feed_item.html'],function(item_tpl){
	'use strict';
	var PlacesFeedItemView = Backbone.View.extend({
		tagName: 'li',
		className: 'place-feed-item',
		template: item_tpl,

		render:function (eventName) {
			$(this.el).html(Mustache.render(item_tpl,this.model.toJSON()));
			return this;
		}
	});

	var PlacesFeedView = Backbone.View.extend({
		tagName: 'ul',
		className: 'places-feed',
		
		initialize: function() {
			this.model.bind('reset',this.render,this);
		},

		render: function(eventName) {
			_.each(this.model.models, function(feeditem) {
				$(this.el).append(new PlacesFeedItemView({model:feeditem}).render().el);
			}, this);
			return this;
		}
	});

	return {
		PlacesFeedView: PlacesFeedView,
		PlacesFeedItemView: PlacesFeedItemView
	};
}); // end require wrapper
