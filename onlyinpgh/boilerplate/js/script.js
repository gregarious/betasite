jQuery(document).ready( function($) {

	// this doesn't get each one, just first first
	/*$('.item').find('.tag-list ul li a').first().css('margin-left', '0');*/

	// Highlight the current menu item based on URL.
	// Alter this so it ignores id paths - i.e. Places is stil highlighted at /places/229

	loc = location.pathname;
	menu_item = $('#site-nav').find('a[href$="'+loc+'"]');
	
	if(menu_item.attr('href') == loc) {
		menu_item.addClass('current-page');
	}

}); // document.ready


