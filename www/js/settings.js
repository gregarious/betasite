(function(root) {
	var obid = root.obid = {};

	var settings = obid.settings = {
		// root url for API calls
		API_URL: "http://scenable.com/apitest/",
		
		// if true, various 
		// TODO: SHOULD BE FALSE (or all traces removed from source) FOR LAUNCH!
		BROWSER_DEBUG: true,
	};

	obid.utils = {
		// returns a URL to be used by a jQuery getJSON call (will automatically
		//  include the JSONP callback) formatting if BROWSER_DEBUG is true)
		to_api: function(relative_url) { 
			var url = settings.API_URL + relative_url; 
			// if in the browser, we need a JSONP request: append callback=? to query string
			if(settings.BROWSER_DEBUG) {
				// if url already has a query string, prefix callback argument with &, otherwise ?
				url += ((relative_url.indexOf('?') === -1) ? '?' : '&') + 'callback=?';				
			}

			return url;
		},
	};
})(window);