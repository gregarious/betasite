// TODO: get Mustache into a proper module 

require(["jquery"], function($) {
    $(function() {
        // all DOM ready code in here
        console.log('ready!');
        $.ajaxSetup({
        	timeout: 5000,
        });
        console.log('AJAX global timeout set to 5s.');
    });
});

