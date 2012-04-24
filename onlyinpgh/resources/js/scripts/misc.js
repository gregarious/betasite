/* Requires jQuery */
$(function(){
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