
jQuery(document).ready( function(){


	// slideToggle the add event/special forms
	// var expand_form = function(title, content) {
	//     $(title).click(function(){
	// 		$(content).slideToggle(500);
	// 	});
	// }

	// expand_form('#openEventForm','#eventForm');
	// expand_form('#openSpecialForm','#specialForm');
	// expand_form('.scheduled-item h4','.scheduled-item > .item-content');



	// Sliding signup sequence

	$('a.shift-panel').click(function () {

		current = $(this).attr('name');
		console.log(current);

		$('.progress span').removeClass('selected');
		$('.progress .'+current).addClass('selected');
		
		$('#site-content').scrollTo($(this).attr('href'), 800);		
		
		return false;
	});

	$(window).resize(function () {
		resizePanel();
	});


	// Item actions

	// $('.item').hover(function(){
	// 	var itemClass = '.' + $(this).attr('class');
	// 	$(itemClass + ' .item-actions').fadeIn(200);
	// 	//console.log(itemClass + ' .item-actions');
	// }, function(){
	// 	$('.item-actions').fadeOut(200);
	// 	//$(this+' .item-actions').fadeOut(200);
	// });

	
	// Where item-1 is unique item id
	$('#item-1 .delete-item').click(function(){
		alert('Are you sure you want to delete #item-1?');
	});

	// Show edit link when hovering over form item
	$('.edit form').hover(function(){
		console.log('asdasd');
		$('.edit-link').fadeIn(200);
	}, function(){
		$('.edit-link').fadeOut(200);
	});

});


function resizePanel() {

	width = $(window).width();
	height = $(window).height();

	mask_width = width * $('.panel').length;
		
	$('#debug').html(width  + ' ' + height + ' ' + mask_width);
		
	$('#site-content, .panel').css({width: width, height: height});
	$('#mask').css({width: mask_width, height: height});
	$('#site-content').scrollTo($('a.selected').attr('href'), 0);
		
}
