/* Requires jQuery */
$(function(){
	// Hide/show single place sections
	var pages = ['#placeInfo', '#placeEvents', '#placeSpecials', '#placeMap', '#placeChatter', '#placeRelated'];

	$.each(pages, function(i, id) {
		$('a.'+id).click(function() {
			$('.related-section').delay(200).hide();
			$(id+'.related-section').fadeIn(200); // Will replace this with a .get();
			$('.related-nav a').removeClass('current-page');
			$(this).addClass('current-page');
		});
	});

	$('#select-sect').change(function(){
		window.location = $(this).val();
	});

}); // document.ready
