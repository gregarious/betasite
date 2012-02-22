define(['jquery'], function($){
    return {
        bind_checkin:   function(node,pid) {
            node.click(function(event){
                console.log('checkin for place'+pid);
                event.preventDefault();
            })
        },
        
        bind_special:   function(node,pid) {
            node.click(function(event){
                console.log('special for place'+pid);
                event.preventDefault();
            })
        },

        bind_favorite:  function(node,pid) {
            node.click(function(event){
                console.log('favorite for place'+pid);
                event.preventDefault();
            })
        },

        bind_directions:    function(node,pid) {
            node.click(function(event){
                console.log('directions for place'+pid);
                event.preventDefault();
            })
        },

        bind_chatter:   function(node,pid) {
            node.click(function(event){
                console.log('chatter for place'+pid);
                event.preventDefault();
            })
        },
    };
});