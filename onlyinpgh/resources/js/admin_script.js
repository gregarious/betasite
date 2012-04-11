
jQuery(document).ready( function(){

    // Sliding create place wizard
    // http://www.queness.com/post/356/create-a-vertical-horizontal-and-diagonal-sliding-content-website-with-jquery
    // $('a.shift-panel').click(function () {

    //  current = $(this).attr('name');
    //  console.log(current);

    //  $('.progress span').removeClass('selected');
    //  $('.progress .'+current).addClass('selected');
        
    //  $('#site-content').scrollTo($(this).attr('href'), 800);     
        
    //  return false;
    // });

    // $(window).resize(function () {
    //  resizePanel();
    // });


    // Item actions

    // Hide and show edit/delete buttons when hovering over item 
    // Is this excessive?
    // $('.item').hover(function(){
    //  var itemId = '.' + $(this).attr('id');
    //  $(itemId + ' .item-actions').fadeIn(200);
    //  //console.log(itemClass + ' .item-actions');
    // }, function(){
    //  $('.item-actions').fadeOut(200);
    //  //$(this+' .item-actions').fadeOut(200);
    // });

    
    // Click X to delete item - need a real function here obvy
    $('.delete-item').click(function(){
        alert('Are you sure you want to delete this item?');
    });

    // Copied from script.js - highlight current menu item based on URL
    loc = location.pathname;
    menu_item = $('#page-nav').find('a[href$="'+loc+'"]');
    
    if(menu_item.attr('href') == loc + '/list') {
        menu_item.addClass('current-page');
    }

    // Datepicker for specials
    $('.datepicker-start, .datepicker-end').datepicker();

    // Datetimepicker for events
    $('.datetimepicker-start').datetimepicker({
        ampm: true,
        stepHour: 1,
        stepMinute: 5,

        onClose: function(dateText, inst) {
            var endBox = $('.datetimepicker-end');
            if (endBox.val() !== '') {
                if(new Date(dateText) > new Date(endBox.val())) {
                    endBox.val(dateText);
                }
            }
            else {
                endBox.val(dateText);
            }
        },
        onSelect: function (selectedDateTime){
            var start = $(this).datetimepicker('getDate');
            $('.datetimepicker-end').datetimepicker('option', 'minDate',
                                                    new Date(start.getTime()) );
        }
    });

    $('.datetimepicker-end').datetimepicker({
        ampm: true,
        stepHour: 1,
        stepMinute: 5,

        onClose: function(dateText, inst) {
            var startBox = $('.datetimepicker-start');
            if (startBox.val() !== '') {
                if(new Date(dateText) < new Date(startBox.val())) {
                    startBox.val(dateText);
                }
            }
            else {
                startBox.val(dateText);
            }
        },
        onSelect: function (selectedDateTime){
            var end = $(this).datetimepicker('getDate');
            $('.datetimepicker-start').datetimepicker('option', 'maxDate',
                                                    new Date(end.getTime()) );

        }
    });

});

// http://www.queness.com/post/356/create-a-vertical-horizontal-and-diagonal-sliding-content-website-with-jquery
function resizePanel() {

    width = $(window).width();
    height = $(window).height();

    mask_width = width * $('.panel').length;
        
    $('#site-content, .panel').css({width: width, height: height});
    $('#mask').css({width: mask_width, height: height});
    $('#site-content').scrollTo($('a.selected').attr('href'), 0);
}
