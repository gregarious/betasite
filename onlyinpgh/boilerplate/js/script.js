
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

	/////////////////
	/// BROADCAST ///
	/////////////////
	
	// Hide the broadcast for 1 secs, then slide down
	$('#broadcast').delay(1000).slideDown(500);

	// Function to cycle through the broadcast items - eventually will be loading new ones
	// http://stackoverflow.com/questions/5258277/rotating-an-unordered-list-automatically-with-jquery
	function rotateBroadcast() {
		var prev = $("#broadcast li:first-child");
		$.unique(prev).each(function(i) {
			$(this).delay(i*1000).slideUp(200, function() {
				$(this).appendTo(this.parentNode).slideDown(200);
			});
		});
	}
	//window.setInterval(rotateBroadcast,5000);

	var pages = ['#placeAtAGlance', '#placeEvents', '#placeSpecials', '#placeMap', '#placeChatter', '#placeRelated'];

	$.each(pages, function(i, id) {
		$('a.'+id).click(function() {
			$('.single-section').delay(200).hide();
			$(id+'.single-section').fadeIn(200); // Will replace this with a .get();
		});
	});


}); // document.ready


