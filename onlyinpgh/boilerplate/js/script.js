

/* Credits:
*** Andi Smith, Using jQuery .on() and .off()
  * http://www.andismith.com/blog/2011/11/on-and-off/
*** Queness, Simple jQuery Modal Window Tutorial
  * http://www.queness.com/post/77/simple-jquery-modal-window-tutorial
*/


jQuery(document).ready( function($) {

	$('.expand-search').click( function() {
		$('#site-search').slideToggle(200);
	});

	$('#expandPostForm').click( function() {
		$('.post-form').slideToggle(200);
	});

	$('.back').click( function() {
		parent.history.back();
		return false;
	});

	var loc = window.location.href;
	$("#site-nav li a").each(function() {
		if(this.href == loc) {
		$(this).addClass('currenthover');
	  }
	});


	/*$('#submitSearch').click(function() {
		printSelectedTags();
	});

	
	// Make main nav select items links - somewhat a hack, will likely need to change
	$('#select-choice-a').change( function() {

		var menuItem = $(this).attr('value');		
		window.location = "/" + menuItem;

	});


	function printSelectedTags() {
		$('#tagSearchChoice option').each( function() {
			$('#searchSummary').text($(this).val());
		});
	}

	$('#expandQuickSearch').click( function() {
		$('.quick-search').slideToggle(300);
	})
		*/
}); // document.ready



/*****************/
/*** BASIC MAP ***/
/*****************/


/*function initializeMap() {

	var latlng = new google.maps.LatLng(40.381423,-80.222168);
	var myOptions = {
		zoom: 12,
		center: latlng,
		mapTypeId: google.maps.MapTypeId.ROADMAP
	};

	var map = new google.maps.Map(document.getElementById('map_canvas'), myOptions);
}*/


