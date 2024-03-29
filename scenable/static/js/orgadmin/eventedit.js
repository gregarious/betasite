// Requires: jQuery, jQuery-autocomplete, jQuery-datetimepicker
$(function(){
    var place_ac_text = $('#id_place-text'),
        place_ac_value = $('#id_place'),
        place_ac_sel_display = $('#id_place-display'),
        place_ac_clear_btn = $('#place-clear'),
        place_ac_spinner = $('#id_place-text').siblings('.spinner');
        place_ac_tip = $('#event-place-tip'),
        place_ac_error_div = $('#id_place-text').siblings('.submit-error');
    
    var tag_ac = $('#id_tags');
    var newplace_dialog_form = $("#newplace-dialog-form"),
        newplace_form_name_input = newplace_dialog_form.find('input[name=newplace-name]');
        newplace_form_address_input = newplace_dialog_form.find('input[name=newplace-address]');
        newplace_form_spinner = $('#newplace-form + .spinner');

    place_ac_spinner.hide();
    place_ac_clear_btn.hide()
        .on('click', function(event){
            onACDeselect();
            $(this).hide();
            return false;
        });
    place_ac_sel_display.hide();

    function onACSelect(ui) {
        place_ac_text.val('').hide();
        place_ac_value.val(ui.item.value);
        place_ac_sel_display.show().html(ui.item.selectedDisplay);
        place_ac_clear_btn.show();
        place_ac_tip.hide();
    }

    function onACDeselect(ui) {
        place_ac_text.val('').show().focus();
        place_ac_value.val('');
        place_ac_sel_display.html('').hide();
        place_ac_clear_btn.hide();
        place_ac_tip.show();
    }

    place_ac_text.autocomplete({
        html: true,
        autoFocus: true,
        minLength: 2,
        
        source: function(request, response) {
            $.ajax({
                url: "/manage/ajax/place_ac/",
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
                                        '<img src=' + item.image_url + ' alt="' + item.name + ' width="50" height="50" />' +
                                    '</div>' +
                                    '<div class="item-content">' +
                                        '<h4 class="item-title">'+ item.name + '</h4>' +
                                        '<p class="address">' + item.address + '</p>' +
                                    '</div></div>',
                            value: item.id,
                            selectedDisplay: item.selected
                        };
                    });
                    responses.push({
                        label: '<p class="ac-item">Place not listed? Create it!</p></div>',
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
            place_ac_error_div.hide();
            place_ac_spinner.show();
        },

        select: function(event, ui) {
            if(ui.item.value === '!newplace') {
                newplace_dialog_form.dialog( "open" );
            }
            else {
                onACSelect(ui);
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
            console.log('change');
            if(!item) {
                onACDeselect();
            }
        }
    });

    newplace_dialog_form.dialog({
        autoOpen: false,
        height: 450,
        width: 350,
        title: "Create a new place",
        modal: true,
        position: "bottom",
        buttons: {
             "Cancel": function() {
                //$('#field').trigger('autocompletechanged');
                $(this).dialog("close");
            },
            "Create": function() {
                var bValid = true;//newplace_form_name_input.val() !== '' || newplace_form_address_input.val() !== '';
                // TODO: any client side validation?
                if ( bValid ) {
                    // dynamically build the form data from the markup itself
                    var formData = {};
                    newplace_dialog_form.find('input')
                                .each(function(){
                                    formData[$(this).attr('name')] = $(this).val();
                                });
                    // send the form via an AJAX request, close form if successful
                    $.ajax({
                        type: 'POST',
                        // grab the URL from the form markup
                        url: newplace_dialog_form.find('form').attr('action'),
                        data: formData,
                        success: function(response) {
                            if(response) {
                                // response from server will be a single JSON object with keys 'id', 'name', 'address'
                                var ui = {
                                    'item': {
                                        'label': '',    // no dropdown, won't be displayed
                                        'value': response['id'],
                                        'selectedDisplay': response['selected']
                                    }
                                };
                                onACSelect(ui);
                                newplace_dialog_form.dialog("close");
                            }
                            else {
                                newplace_dialog_form.find('.submit-error').html('<i>server error (code 2)<i>').show();
                            }
                        },
                        error: function(jqXHR, textStatus, errorThrown) {
                            newplace_dialog_form.find('.submit-error').html('<i>server error (code 1)<i>').show();
                        },
                        complete: function(jqXHR, textStatus) {
                            newplace_dialog_form.find('.spinner').hide();
                        }
                    });
                    newplace_dialog_form.find('.submit-error').hide();
                    newplace_dialog_form.find('.spinner').show();
                }
                else {
                    // TODO: inform user to input a name or location
                }
            }
        }
    });

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

    // Temporary global export of the on AC select function
    if (typeof scenable === 'undefined') {
        scenable = {};
    }
    scenable.onACSelect = onACSelect;
});