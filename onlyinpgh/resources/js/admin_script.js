
jQuery(document).ready( function(){
    // Copied from script.js - highlight current menu item based on URL
    loc = location.pathname;
    menu_item = $('#page-nav').find('a[href$="'+loc+'"]');
    
    if(menu_item.attr('href') == loc + '/list') {
        menu_item.addClass('current-page');
    }
});
