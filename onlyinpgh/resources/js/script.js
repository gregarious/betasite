$(function() {
if(typeof(Scenable) === 'undefined') {
	Scenable = {};
	Scenable.userActions = {
		favoritePlace: function() {

			},
		attendEvent: function() {

			}
	};
}

// this doesn't get each one, just first first
/*$('.item').find('.tag-list ul li a').first().css('margin-left', '0');*/

// Highlight the current menu item based on URL.
// Alter this so it ignores id paths - i.e. Places is stil highlighted at /places/229
// loc = location.pathname;
// menu_item = $('.main-menu').find('a[href$="'+loc+'"]');

// if(menu_item.attr('href') == loc) {
// 	menu_item.addClass('current-page');
// }

// For mobile dropdown, select option with same value as URL
// option = $('#scene-nav select').find('option[value$="'+window.location+'"]');
	
// if(option.attr('value') == window.location) {
// 	option.attr('selected', 'selected');
// }

// Hide/show single place sections
var pages = ['#placeDetail', '#placeEvents', '#placeSpecials'];

$.each(pages, function(i, id) {
	$('a.'+id).click(function() {
		$('.detail-section').delay(200).hide();
		$(id+'.detail-section').fadeIn(200); // Will replace this with a .get();
		$('.detail-nav a').removeClass('current-page');
		$(this).addClass('current-page');
	});
});

$('#select-sect').change(function(){
	window.location = $(this).val();
});

}); // document.ready
