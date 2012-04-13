define(['jquery'], function($){
    function toggleFavorite(pid,toggleOn) {
        var action = toggleOn ? 'addfav' : 'removefav';
            request = $.getJSON('#',{action:action});
            settingFavorite = $.Deferred();

        // TODO: any way to use pipe() for the logic below?
        request.done(function(data) {
            // TODO: handle invalid JSON response format
            if (data.status === 'success') {
                settingFavorite.resolve(data.msg);
            } else {
                settingFavorite.reject(data.msg);
            }
        });

        request.fail(function(jqXHR, textStatus, errorThrown, dummy, dummy2) {
            // TODO: handle invalid JSON response format
            settingFavorite.reject(textStatus);
        });

        return settingFavorite;
    }

    // module interface begin
    return {
        /* 
         * setFavorite:
         *  Sends an AJAX request to the server to mark the given place id as 
         *      the current user's favorite.
         *  Returns a jQuery Promise object that will indicate the status of the request.
        */
        addFavorite: function(pid) {
            return toggleFavorite(pid,true);
        },
        removeFavorite: function(pid) {
            return toggleFavorite(pid,false);
        },

    //     bind_checkin:   function(node,pid) {
    //         node.click(function(event){
    //             $.getJSON('#',{action:'checkin'},function(json){
    //                 if(json.status == 'success') {
    //                     console.log('checkin success!');
    //                 }
    //                 else if(json.status == 'failure') {
    //                     console.log('error: ' + json.error)
    //                 }
    //                 else {
    //                     console.log('unknown response: '+json)
    //                 }
    //             });
    //             event.preventDefault();
    //         });
    //     },
        
    //     bind_favorite:  function(node,pid) {
    //         node.click(function(event){
    //             console.log('favorite for place'+pid);
    //             event.preventDefault();
    //         })
    //     },
    };
});