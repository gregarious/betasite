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

	//Show/hide .item-content when hovering over now thumbnail items
	// $('.item.short').hover(function(){
	// 	$(this).find('.item-type').fadeIn(200);
	// }, function() {
	// 	$(this).find('.item-type').fadeOut(270);
	// });

    // Sidebar feedback modal
	$('.feedback-modal').dialog({
        modal: true,
        autoOpen: false
    });

    $('#openFeedbackModal').click(function(){
        $('.feedback-modal').dialog("open");
    });

    var feedbackForm = $('.feedback-modal').find('form');
    feedbackForm.find('input[type="submit"]').click(function(){
        $.ajax({
            url: scenable.constants.SITE_URL + 'feedback/ajax/generic/',
            type: 'POST',
            data: {
                'feedback': feedbackForm.find('textarea[name="feedback"]').val(),
                'csrfmiddlewaretoken': feedbackForm.find('input[name="csrfmiddlewaretoken"]').val()
            }
        });
        $('.feedback-modal').dialog("close");
        return false;
    });

    // Show 'private' or 'public' next to checkbox in manage account panel
    // For later. 
    // if ($('#account-privacy input[type="checkbox"]').is(':checked')) {
    //     $('.check-value').html('Public');
    //     $(this).change(function() {
    //     	$('.check-value').html('Private');
    //     });

    //     console.log('check!');
    // } else {
    // 	$('.check-value').html('Private');
    // 	$(this).change(function() {
    //     	$('.check-value').html('Public');
    //     });
    // }
    


}); // document.ready
