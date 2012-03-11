// Main entrypoint for all JS

// We assume the following globals are available via previous script loading:
// $, jQuery, Mustache, Backbone

function debugStart() {
    gettingData = $.getJSON(obid.utils.to_api('places/app/284'));
    gettingData.done( function(data) {
         $('#container').html('this:'+Mustache.render(singleTemplate,data));
    });
    gettingData.fail( function(jqXHR, textStatus, errorThrown) {
         alert('Problem contacting server: '+textStatus);
    });
    
    var singleTemplate = '<div id="wrapper" class="single">{{place.name}}</div>';
}

$(function() {
    console.log('DOM ready!');
    $(document).on('deviceready',function(){  // ensure phonegap API is hooked up to device
        console.log('device ready!');
        $.ajaxSetup({
            timeout: 5000,
        });
        console.log('AJAX global timeout set to 5s.');
        debugStart();        
    });

// ONLY FOR BROWSER TESTING: ALWAYS DISABLE WHEN RUN WITH PHONEGAP!!!
    $(document).trigger('deviceready');   
});
