
jQuery(document).ready( function($) {

	// this doesn't get each one, just first first
	/*$('.item').find('.tag-list ul li a').first().css('margin-left', '0');*/

	// Highlight the current menu item based on URL.
	// Alter this so it ignores id paths - i.e. Places is stil highlighted at /places/229

	loc = location.pathname;
	menu_item = $('.main-menu').find('a[href$="'+loc+'"]');
	
	if(menu_item.attr('href') == loc) {
		menu_item.addClass('current-page');
	}

	// Hide the broadcast for 1 sec, then slide down - only on home page
	//$('#site-sidebar').hide().delay(1000).slideDown(500);

	// Hide/show single place sections
	var pages = ['#placeAtAGlance', '#placeEvents', '#placeSpecials', '#placeMap', '#placeChatter', '#placeRelated'];

	$.each(pages, function(i, id) {
		$('a.'+id).click(function() {
			$('.related-section').delay(200).hide();
			$(id+'.related-section').fadeIn(200); // Will replace this with a .get();
		});
	});

	// Float odd feed items right to allow for columns.
	$('.feed .item:even').addClass('left');
	$('.feed .item:odd').addClass('right');

}); // document.ready
