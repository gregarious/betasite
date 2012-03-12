/*global Backbone, _ */
/*jshint browser:true */
/*jshint devel:true */

(function(root) {
	'use strict';
	var obid = root.obid = {};

	// if true, various settings will be changed to allow debugging in the browser (e.g. JSONP requests)
	// TODO: SHOULD BE FIXED TO FALSE (or all traces removed from source) FOR LAUNCH!
	// total hack the way it's done here -- e.g. won't work for Android simulators
	var BROWSER_DEBUG = navigator.userAgent.toLowerCase().search('iphone') === -1;

	var settings = obid.settings = {
		// root url for API calls
		API_URL: "http://127.0.0.1:8000/",
		
		BROWSER_DEBUG: BROWSER_DEBUG
	};

	obid.utils = {
		// returns a URL to be used by a jQuery getJSON call (will automatically
		//  include the JSONP callback) formatting if BROWSER_DEBUG is true)
		to_api: function(relative_url) {
			return settings.API_URL + relative_url;
		}
	};
})(window);