/* Requires jQuery, underscore, Backbone, google maps api */
scenable = window.scenable = window.scenable || {};

scenable.map = {
    mapFactory: function(mapType, domElement, mapOptions) {
        var defaultOpts = {
            mapTypeId: google.maps.MapTypeId.ROADMAP,
            panControl: false,
            mapTypeControl: false,
            streetViewControl: false,
            zoomControl: true,
            zoomControlOptions: {
                style: google.maps.ZoomControlStyle.SMALL,
                position: google.maps.ControlPosition.TOP_RIGHT
            }
        };
        if(mapType === 'single') {
            _.extend(defaultOpts, {
                zoom: 16
            });
        }
        if(mapType === 'feed') {
            _.extend(defaultOpts, {
                zoom: 14
            });
        }
        return new google.maps.Map(domElement,
            _.defaults(mapOptions,defaultOpts));
    }
};