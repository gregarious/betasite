jQuery(document).ready( function(){

	// slideToggle the add event/special forms
	var expand_form = function(title, content) {
	    $(title).click(function(){
			$(content).slideToggle(500);
		});
	}

	expand_form('#openEventForm','#eventForm');
	expand_form('#openSpecialForm','#specialForm');
	expand_form('.scheduled-item h4','.scheduled-item > .item-content');

	// Sliding signup sequence

	$('a.panel').click(function () {

		current = $(this).attr('name');
		console.log(current);

		$('.progress span').removeClass('selected');
		$('article.'+current+' .progress .'+current).addClass('selected');
		
		$('#wrapper').scrollTo($(this).attr('href'), 800);		
		
		return false;
	});

	$(window).resize(function () {
		resizePanel();
	});
	
});

function resizePanel() {

	width = $(window).width();
	height = $(window).height();

	mask_width = width * $('.item').length;
		
	$('#debug').html(width  + ' ' + height + ' ' + mask_width);
		
	$('#wrapper, .item').css({width: width, height: height});
	$('#mask').css({width: mask_width, height: height});
	$('#wrapper').scrollTo($('a.selected').attr('href'), 0);
		
}