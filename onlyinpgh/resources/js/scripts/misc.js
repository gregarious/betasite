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

	// Make mobile select box menu links
	$('#select-sect').change(function(){
		window.location = $(this).val();
	});

	// Show/hide .item-content when hovering over now thumbnail items
	$('.item.short').hover(function(){
		$(this).find('.item-content').fadeIn(200);
	}, function() {
		$(this).find('.item-content').fadeOut(270);
	});

	// Grabbit modal
    $('.grabbit-modal').dialog({
        maxHeight: 500,
        modal: true,
        autoOpen: false,
    });

    $('#openGrabbitModal').click(function(){
        $('.grabbit-modal').dialog("open");
    });

    // Sidebar feedback modal
	$('.feedback-modal').dialog({
        maxHeight: 700,
        modal: true,
        autoOpen: false
    });

    $('#openFeedbackModal').click(function(){
        $('.feedback-modal').dialog("open");
    });    

}); // document.ready
