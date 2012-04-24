/* Requires jQuery, underscore, yepnope */
$(function(){
    window.Scenable = window.Scenable || {};
    window.Scenable.feed = {
        /* to be called after a map has been created with it's markers */
        linkFeedToMap: function(domElements, map) {
            _.each(_.zip(domElements,map.mapItems), function(pkg) {
                var el = pkg[0], item = pkg[1];
                $(el).data('mapItem', item)     // store it for the hell of it
                     .click(function(event){
                        /* on click, trigger the linked marker's click event and
                           ensure only the clicked element has the focus class */
                        google.maps.event.trigger(item.marker, 'click');
                        _.each(domElements, function(el) {
                            $(el).removeClass('focused');
                        });
                        $(el).addClass('focused');
                     });

            });
        },
        // constructor for a feed map
        Map: function(domElement, lat, lng, zoom) {
            var myOptions = {
                center: new google.maps.LatLng(lat, lng),
                zoom: zoom || 14,
                mapTypeId: google.maps.MapTypeId.ROADMAP,
                panControl: false,
                mapTypeControl: false,
                streetViewControl: false,
                zoomControl: true,
                zoomControlOptions: {
                    style: google.maps.ZoomControlStyle.SMALL
                }
            };
            // "private" variables for the new object
            var _map = new google.maps.Map(domElement, myOptions);
            var _bounds = new google.maps.LatLngBounds();
            var _activeItem = null;
            /* return a new feed map with marker setting capabilities */
            return {
                mapItems: [],
                /* returns a marker+iw object */
                addItem: function(lat, lng, iwContent, icon, shadowIcon) {
                    var pos = new google.maps.LatLng(lat, lng);
                    var mapItem = {
                        marker: new google.maps.Marker({
                            position: pos,
                            icon: icon,
                            shadow: _.isUndefined(shadowIcon) ? null : shadowIcon,
                            map: _map
                        }),
                        infoWindow: new google.maps.InfoWindow({
                          content: iwContent
                        }),
                        onFocus: function() {
                            this.infoWindow.open(_map, this.marker);
                            _activeItem = this;
                        },
                        onBlur: function() {
                            this.infoWindow.close();
                            _activeItem = null;
                        }
                    };
                    // need to pass the full mapItem when a marker.click event is fired
                    google.maps.event.addListener(mapItem.marker, 'click', function(){
                        if(_activeItem) {
                            if(_activeItem === mapItem) {
                                return;
                            }
                            _activeItem.onBlur();
                        }
                        _activeItem = mapItem;
                        _activeItem.onFocus();
                    });
                    this.mapItems.push(mapItem);
                    _bounds.extend(pos);
                    _map.fitBounds(_bounds);
                },
                removeItem: function(idx) {
                    var mapItem = this.mapItems.splice(idx,1)[0];
                    mapItem.marker.setMap(null);
                }
            };
        }
    };
});