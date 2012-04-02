
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

	// For mobile dropdown, select option with same value as URL
	// option = $('#scene-nav select').find('option[value$="'+window.location+'"]');
		
	// if(option.attr('value') == window.location) {
	// 	option.attr('selected', 'selected');
	// }

	// Hide the broadcast for 1 sec, then slide down - only on home page
	//$('#site-sidebar').hide().delay(1000).slideDown(500);

	// Hide/show single place sections
	var pages = ['#placeInfo', '#placeEvents', '#placeSpecials', '#placeMap', '#placeChatter', '#placeRelated'];
	
	$.each(pages, function(i, id) {
		$('a.'+id).click(function() {
			$('.related-section').delay(200).hide();
			$(id+'.related-section').fadeIn(200); // Will replace this with a .get();
		});
	});

	$('#scene-nav select').change(function(){
		window.location = $(this).attr('value');
	});

	//window.location = $(this).find("option:value").val();
	


	// Make menu a dropdown for mobile
	// http://css-tricks.com/convert-menu-to-dropdown/
	// $("<select />").appendTo("#scene-nav");

	// // Create default option "Go to..."
	// $("<option />", {
	//    "selected": "selected",
	//    "value"   : "",
	//    "text"    : "Go to..."
	// }).appendTo("#scene-nav select");

	// // Populate dropdown with menu items
	// $("#scene-nav a").each(function() {
	//  var el = $(this);
	//  $("<option />", {
	//      "value"   : el.attr("href"),
	//      "text"    : el.text()
	//  }).appendTo("nav select");
	// });

	// $("#scene-nav select").change(function() {
	//   window.location = $(this).find("option:selected").val();
	// });

}); // document.ready
