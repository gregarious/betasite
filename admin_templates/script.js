$(document).ready( function(){

	// slideToggle the add event/special forms
	var expand_form = function(title, content) {
	    $(title).click(function(){
			$(content).slideToggle(500);
		});
	}

	expand_form('#openEventForm','#eventForm');
	expand_form('#openSpecialForm','#specialForm');

});