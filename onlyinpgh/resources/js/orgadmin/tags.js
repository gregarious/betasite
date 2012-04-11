// Requires: jQuery, jQuery-autocomplete
$(function(){
    if (typeof scenable === 'undefined') {
        scenable = {};
    }

    scenable.activateTagAC = function (selector, tagNames) {
        function split( val ) {
            return val.split( /,\s*/ );
        }
        function extractLast( term ) {
            return split( term ).pop();
        }

        $(selector)
            .on( "keydown", function( event ) {
                if((event.keyCode === $.ui.keyCode.TAB ||
                    event.keyCode === $.ui.keyCode.ENTER) &&
                    $(this).data("autocomplete").menu.active ) {
                        event.preventDefault();
                    }
            })
            .autocomplete({
                minLength: 1,
                delay: 0,
                autoFocus: true,
                html: true,
                source: function( request, response ) {
                    var term = extractLast( request.term );
                    if(term.replace(/\s/g,'').length === 0) {
                        response([]);
                        return false;
                    }
                    var re = $.ui.autocomplete.escapeRegex(term);
                    var matcher = new RegExp( "^" + re, "i" );
                    var matches = $.grep(tagNames, function(item,index){
                        return matcher.test(item);
                    }).slice(0,4);
                    response( $.map( matches, function(item) {
                        return {
                            value: item,
                            label: item.replace(matcher, '<b>'+term+'</b>')
                        };
                    }));
                },
                focus: function() {
                    // prevent value inserted on focus
                    return false;
                },
                select: function( event, ui ) {
                    var terms = split( this.value );
                    // remove the current input
                    terms.pop();
                    // add the selected item
                    terms.push( ui.item.value );
                    // add placeholder to get the comma-and-space at the end
                    terms.push( "" );
                    this.value = terms.join( ", " );
                    return false;
                }
            });
    };
});

