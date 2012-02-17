$(document).ready( function(){

	console.log('loaded');
	// helper function that binds view loaders to the current element
	var expand_form = function(title, content) {
	    $(title).click(function(){
			$(content).slideToggle(500);
		});
	}

	expand_form('#openEventForm','#eventForm');
	expand_form('#openSpecialForm','#specialForm');

	/*$('#openEventForm').click(function(){
		$('#eventForm').slideToggle(200);
	});
*/

});