/* Requires jQuery */
scenable = window.scenable = window.scenable || {};

scenable.useractions = {
    _ensureState: function($el, isOn) {
        if(isOn) {
            $el.children('.state-on').show();
            $el.children('.state-off').hide();
        }
        else {
            $el.children('.state-off').show();
            $el.children('.state-on').hide();
        }
    },

    _attachAtomicHandler: function(ajaxActionElement, ajaxData, url, actions, isOn) {
        var $el = $(ajaxActionElement);
        isOn = _.isUndefined(isOn) ? $el.children('.state-on').is(":visible") : isOn;
        scenable.useractions._ensureState($el, isOn);
        // redundant sanity check to ensure markup is consistant with code state
        $el.children('.state-pending').hide();
        var currentAction = isOn ? actions[0] : actions[1];
        var locked = false;
        var processingAction = $.Deferred().resolve();
        $el.click(function(event){
            if(locked || processingAction.state() === 'pending') {
                // somehow a duplicate action got in. do nothing.
                return false;
            }

            var data = _.extend(_.clone(ajaxData),{'action': currentAction});
            processingAction = $.ajax({
                url: url,
                data: data,
                type: 'GET'
            });

            processingAction.done(function(data){
                if(data.success) {
                    isOn = !isOn;
                    scenable.useractions._ensureState($el, isOn);
                    $el.children('.state-pending').hide();
                    currentAction = isOn ? actions[0] : actions[1];
                }
                else {
                    $el.children('.state-process').text('error');
                    locked = true;
                }
            });
            processingAction.fail(function(jqXHR, textStatus) {
                $el.children('.state-pending').text(textStatus);
                locked = true;
            });

            $el.children('.state-off').hide();
            $el.children('.state-on').hide();
            $el.children('.state-pending').text('processing...').show();

            return false;
        });        
    },

    attachFavoriteHandler: function(ajaxActionElement, placeId, isOn) {
        scenable.useractions._attachAtomicHandler(
            ajaxActionElement, 
            {'pid': placeId},
            '/places/ajax/favorite/',
            ['unfavorite', 'favorite'],
            isOn
        );
    },

    attachAttendanceHandler: function(ajaxActionElement, eventId, isOn) {
      scenable.useractions._attachAtomicHandler(
            ajaxActionElement, 
            {'eid': eventId},
            '/events/ajax/attend/',
            ['unattend', 'attend'],
            isOn
        );  
    },

    buyCoupon: function(specialId) {

    },
    viewCoupon: function(couponId) {

    },
    markCouponUsed: function(couponId) {

    },
};