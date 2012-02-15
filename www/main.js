// Main script file that contains all plumbing for loading/render templates

// temporary global
//APP_SERVER = 'http://www.bloodypajamas.com'
APP_SERVER = 'http://127.0.0.1:8000'

// Main view loading function. Will replace the html contents of 
// the given element with the rendered view specified.
//  * element: jQuery object whose html content will be replaced
//  * vname: name of view to load (should match script filename in vloaders directory)
//  * data: additional data to be passed to the view (e.g. GET args for AJAX calls)
function load_view(vname,element,data) {
    // ensure 'views' namespace exists
    if(typeof vloaders == 'undefined') {
        vloaders = {};
    }

    var render_view = function() {
        // replace element html with view contents
        element.hide();
        vloaders[vname].render(element,data);
        element.show();
    }

    // get loader object if it has not yet been put into the vloaders namespace
    if(typeof vloaders[vname] == 'undefined') {
        $.getScript('vloaders/'+vname+'.js')
            .done(
                function() {
                    vloaders[vname].init();
                    render_view();
                })
            .fail(
                function(jqxhr, settings, exception) {
                    console.log([jqxhr, settings, exception]);
                    element.html('error');
                });
    }
    else {
        render_view();    
    }
}

// from http://floatlearning.com/2011/05/how-well-does-phonegap-scale/
function render_template(tname,data,callback) {
    if(!ich.templates[tname]) {
        var tfile = "templates/" + tname + ".html" 
        // If the template doesn't exist, load it from templates/[name].html
        $.get(tfile,function(template) {
                ich.addTemplate(tname,template);
                callback.call(null,ich[tname](data),data);
            });
    } 
    else {
        // The template has already been loaded; we'll use the cached template information
        callback.call(null,ich[tname](data),data);
    }
}
