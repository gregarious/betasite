/*global Backbone, _, $, Mustache, require, define */
/*jshint browser:true */
/*jshint devel:true */

define(['text!../../templates/nav_header.html'],function(nav_tpl){
	'use strict';

	return {
		NavHeader: Backbone.View.extend({
			tagName: 'nav',
			id: 'nav-header',
			template: nav_tpl,

			render: function(eventName){
				$(this.el).html(nav_tpl);	// no template rendering needed as of yet
				return this;
			},

			events: {
				// TODO: insert back link event
				'click #places-link': function(event) {
					window.app.navigate('places', true);
					return false;
				},
				'click #events-link': function(event) {
					window.app.navigate('events', true);
					return false;
				},
				'click #specials-link': function(event) {
					window.app.navigate('specials', true);
					return false;
				}
			}
		})
	};
});