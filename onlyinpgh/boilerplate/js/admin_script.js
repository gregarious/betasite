
jQuery(document).ready( function(){

	// Sliding create place wizard
	// http://www.queness.com/post/356/create-a-vertical-horizontal-and-diagonal-sliding-content-website-with-jquery
	// $('a.shift-panel').click(function () {

	// 	current = $(this).attr('name');
	// 	console.log(current);

	// 	$('.progress span').removeClass('selected');
	// 	$('.progress .'+current).addClass('selected');
		
	// 	$('#site-content').scrollTo($(this).attr('href'), 800);		
		
	// 	return false;
	// });

	// $(window).resize(function () {
	// 	resizePanel();
	// });


	// Item actions

	// Hide and show edit/delete buttons when hovering over item 
	// Is this excessive?
	// $('.item').hover(function(){
	// 	var itemId = '.' + $(this).attr('id');
	// 	$(itemId + ' .item-actions').fadeIn(200);
	// 	//console.log(itemClass + ' .item-actions');
	// }, function(){
	// 	$('.item-actions').fadeOut(200);
	// 	//$(this+' .item-actions').fadeOut(200);
	// });

	
	// Click X to delete item - need a real function here obvy
	$('.delete-item').click(function(){
		alert('Are you sure you want to delete this item?');
	});

	// Copied from script.js
	loc = location.pathname;
	menu_item = $('#page-nav').find('a[href$="'+loc+'"]');
	
	if(menu_item.attr('href') == loc) {
		menu_item.addClass('current-page');
	}

	$('.datepicker-start').datetimepicker({
		ampm: true,
		stepHour: 1,
		stepMinute: 5,
		dateFormat: 'MM d,',


	    onClose: function(dateText, inst) {
	        var endDateTextBox = $('.datepicker-end');
	        if (endDateTextBox.val() != '') {
	            var testStartDate = new Date(dateText);
	            var testEndDate = new Date(endDateTextBox.val());
	            if (testStartDate > testEndDate)
	                endDateTextBox.val(dateText);
	        }
	        else {
	            endDateTextBox.val(dateText);
	        }
	    },
	    onSelect: function (selectedDateTime){
	        var start = $(this).datetimepicker('getDate');
	        $('.datepicker-end').datetimepicker('option', 'minDate', new Date(start.getTime()));
	    }
	});

	$('.datepicker-end').datetimepicker({
		ampm: true,
		stepHour: 1,
		stepMinute: 5,
		dateFormat: 'MM d,',

	    onClose: function(dateText, inst) {
	        var startDateTextBox = $('.datepicker-start');
	        if (startDateTextBox.val() != '') {
	            var testStartDate = new Date(startDateTextBox.val());
	            var testEndDate = new Date(dateText);
	            if (testStartDate > testEndDate)
	                startDateTextBox.val(dateText);
	        }
	        else {
	            startDateTextBox.val(dateText);
	        }
	    },
	    onSelect: function (selectedDateTime){
	        var end = $(this).datetimepicker('getDate');
	        $('.datepicker-start').datetimepicker('option', 'maxDate', new Date(end.getTime()) );
	    }
	});

});

// http://www.queness.com/post/356/create-a-vertical-horizontal-and-diagonal-sliding-content-website-with-jquery
function resizePanel() {

	width = $(window).width();
	height = $(window).height();

	mask_width = width * $('.panel').length;
		
	$('#site-content, .panel').css({width: width, height: height});
	$('#mask').css({width: mask_width, height: height});
	$('#site-content').scrollTo($('a.selected').attr('href'), 0);
		
}
