// Requires: jQuery, jQuery-autocomplete
$(function(){
    var place_ac_text = $('#id_place-text'),
        place_ac_value = $('#id_place'),
        place_ac_clear_btn = $('#place-clear'),
        place_ac_spinner = $('.spinner'),
        place_ac_confirmbox = $('#confirm-box'),
        place_ac_confirmcontent = $('#confirm-content'),
        place_ac_error_div = $('.submit-error');
    place_ac_spinner.hide();
    place_ac_clear_btn.hide()
        .on('click', function(event){
            on_ac_deselect();
            $(this).parent().find('#id_place-text').focus();
            return false;
        });

    function on_ac_select(ui) {
        place_ac_text.val(ui.item.selectedLabel);
        place_ac_value.val(ui.item.value);
        place_ac_clear_btn.show();
        $("form :submit").removeAttr('disabled');
        $(".field-container").fadeOut(200);
        $.ajax({
            url: "/manage/ajax/place_confirm/",
            dataType: 'html',
            data: {
                'pid': ui.item.value
            },
            timeout: 3000,
            success: function(html_response) {
                place_ac_confirmcontent.html(html_response);
            },
            error: function(jqXHR, textStatus, errorThrown) {
                place_ac_confirmcontent.html(ui.item.selectedLabel);
            },
            complete: function(jqXHR, textStatus) {
                place_ac_confirmbox.delay(200).fadeIn(200);
                $('form').css('margin-top', '0');
            }
        });
    }

    function on_ac_deselect(ui) {
        place_ac_text.val('');
        place_ac_value.val('');
        remove_confirmation();
    }

    function remove_confirmation() {
        place_ac_confirmbox.fadeOut(200);
        place_ac_clear_btn.hide();
        $("form :submit").attr('disabled',true);
        $("form").css('margin-top', '2em');
        $(".field-container").delay(200).fadeIn(200);
    }

    place_ac_text.autocomplete({
        html: true,
        autoFocus: true,
        minLength: 2,
        
        source: function(request, response) {
            $.ajax({
                url: "/manage/ajax/placeclaim_ac/",
                dataType: 'json',
                data: {
                    'term': request.term
                },
                timeout: 3000,
                success: function(data) {
                    responses = $.map(data, function(item) {
                        return {
                            label: '<div class="ac-item">' +
                                    '<div class="item-thumb">' +
                                        '<img src=' + item.image_url + ' alt="' + item.name + ' height="50" width="50" />' +
                                    '</div>' +
                                    '<div class="item-content">' +
                                        '<h4 class="item-title">'+ item.name + '</h4>' +
                                        '<p class="address">' + item.address + '</p>' +
                                    '</div></div>',
                            value: item.id,
                            selectedLabel: item.name
                        };
                    });
                    responses.push({
                        label: '<div class="ac-item"><p>Place not listed? Create it!</p></div>',
                        value:'!newplace'
                    });
                    response(responses);
                },
                error: function(jqXHR, textStatus, errorThrown) {
                    place_ac_error_div.html('<i>server error (code 1)<i>').show();
                },
                complete: function(jqXHR, textStatus) {
                    place_ac_spinner.hide();
                }
            });
        },
        
        search: function(event, ui) {
            remove_confirmation();
            place_ac_spinner.show();
            place_ac_error_div.hide();
        },

        select: function(event, ui) {
            if(ui.item.value === '!newplace') {
                window.location.href = "/manage/places/setup/new/";
            }
            else {
                on_ac_select(ui);   // function will show the confirmation dialog
            }
            return false;
        },

        focus: function(event, ui) {
            return false;   // makes it so text doesn't show up in form till selection
        },

        change: function(event, ui) {
            // if something was changed in the text field after a select, the selectedItem will be 
            // cleared out. If no selected item, the inputs get reset.
            var item = $(this).data().autocomplete.selectedItem;
            if(!item) {
                on_ac_deselect();
            }
        }
    });
});