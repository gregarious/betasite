/*global Backbone */
(function() {
	'use strict';
	// Backbone.syncJSONP forces the use of a JSONP request for each sync operation
	Backbone.syncJSONP = function(method,model,options) {
		options.dataType = 'jsonp';
		Backbone.sync.call(this,method,model,options);
	};
})();