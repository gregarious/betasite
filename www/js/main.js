// Main entrypoint for all JS

// We assume the following globals are available via previous script loading:
// $, jQuery, Mustache, Backbone, obid

function debugStart() {
    gettingData = $.getJSON(obid.utils.to_api('places/app/284'));
    gettingData.done( function(data) {
         $('#container').html(Mustache.render(singleTemplate,data));
    });
    gettingData.fail( function(jqXHR, textStatus, errorThrown) {
         alert('Problem contacting server: '+textStatus);
    });
    
    var singleTemplate = '<div id="wrapper" class="single">{{place.name}}</div>';
}

$(function() {
    console.log('DOM ready!');
    console.log('BROWSER_DEBUG: ' + obid.settings.BROWSER_DEBUG);
    $(document).on('deviceready',function(){  // ensure phonegap API is hooked up to device
        console.log('device ready!');
        $.ajaxSetup({
            timeout: 5000,
        });
        console.log('BROWSER_DEBUG: ' + obid.settings.BROWSER_DEBUG);
        console.log('AJAX global timeout set to 5s.');
        debugStart();        
    });

    // if we're debugging in the browser, manually call this
    if(obid.settings.BROWSER_DEBUG) {
        $(document).trigger('deviceready'); 
    }
});
