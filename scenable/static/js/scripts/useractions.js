/* Requires jQuery, underscore */
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

    // TODO: this setup is a bit too rushed for my tastes. begging for a Backbone impl with a good api.
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
                type: 'GET',
                timeout: 4000
            });

            processingAction.done(function(data){
                if(data.success) {
                    isOn = !isOn;
                    scenable.useractions._ensureState($el, isOn);
                    $el.children('.state-pending').hide();
                    currentAction = isOn ? actions[0] : actions[1];
                }
                else {
                    $el.children('.state-pending').text('error');
                    locked = true;
                }
            });
            processingAction.fail(function(jqXHR, textStatus) {
                $el.children('.state-pending').text(textStatus);
                locked = true;
            });

            $el.children('.state-off').hide();
            $el.children('.state-on').hide();
            $el.children('.state-pending').show();

            return false;
        });
    },

    attachFavoriteHandler: function(ajaxActionElement, placeId, isOn) {
        scenable.useractions._attachAtomicHandler(
            ajaxActionElement,
            {'pid': placeId},
            '/oakland/places/ajax/favorite/',
            ['unfavorite', 'favorite'],
            isOn
        );
    },

    attachAttendanceHandler: function(ajaxActionElement, eventId, isOn) {
      scenable.useractions._attachAtomicHandler(
            ajaxActionElement,
            {'eid': eventId},
            '/oakland/events/ajax/attend/',
            ['unattend', 'attend'],
            isOn
        );
    },

    attachCouponBuyHandler: function(grabElement, specialId, modalPopupElement) {
        var $el = $(grabElement);
        $el.one('click', function(){
            var processingAction = $.ajax({
                url: '/oakland/specials/ajax/buy/',
                data: {
                    sid: specialId
                },
                type: 'GET',
                timeout: 4000
            });

            $el.text('Processing...');
            processingAction.done(function(data){
                // ignore errors that say the coupon has already been bought
                if(data.success && data.success.uuid) {
                    $el.text('Got It!');
                    var openPopup = function() {
                        scenable.useractions.openCouponPopup(modalPopupElement, data.success.uuid);
                    };
                    $el.on('click', openPopup);
                    openPopup();
                }
                else {
                    $el.text('error');
                }
            });
            processingAction.fail(function(jqXHR, textStatus){
                $el.text(textStatus);
            });
        });
    },

    openCouponPopup: function(modalPopupElement, couponUUID) {
        var $el = $(modalPopupElement);
        $el.find('#emailCoupon')
            .off('click')
            .on('click', function(){
                scenable.useractions.emailCoupon(couponUUID, $el);
            });

        $el.find('#printCoupon')
            .off('click')
            .on('click', function(){
                scenable.useractions.printCoupon(couponUUID);
                $el.dialog('close');
            });
            
        $el.dialog({
            maxHeight: 500,
            modal: true,
            autoOpen: false
        });
       $el.dialog('open');
    },

    emailCoupon: function(couponUUID, popupEl) {
        var sending = $.ajax({
            url: '/oakland/specials/ajax/email/',
            data: {
                uuid: couponUUID
            },
            type: 'GET',
            timeout: 8000
        });

        if(popupEl) {
            var $el = $(popupEl).find('#emailStatus');
            $el.text('Sending...');
            sending.done(function(data){
                if(data.success) {
                    $el.text('Sent!');
                }
                else {
                    $el.text('error');
                }
            });
            sending.error(function(){
                $el.text('error');
            });
        }
    },

    printCoupon: function(couponUUID) {
        window.open('/oakland/specials/redeem/' + couponUUID + '/?print=yes');
    },

    markCouponUsed: function(couponUUID) {
        console.print('marking as used '+couponUUID);
    }
};