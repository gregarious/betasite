/*global Backbone, _, $, Mustache, require, define */
/*jshint browser:true */
/*jshint devel:true */

define(['text!../../templates/places/detail.html'],function(detail_tpl){
	'use strict';
	var PlaceDetailView = Backbone.View.extend({
		tagName: 'div',
		className: 'single',
		template: detail_tpl,

		render:function (eventName) {
			$(this.el).html(Mustache.render(detail_tpl,this.model.toJSON()));
			return this;
		}
	});

	return {
		PlaceDetailView: PlaceDetailView
	};
}); // end require wrapper
