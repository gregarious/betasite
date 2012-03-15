from onlyinpgh.common.core.viewmodels import ViewModel

from onlyinpgh.places.models import Place
from onlyinpgh.identity.models import FavoriteItem

from onlyinpgh.common.viewmodels import FeedCollection

from onlyinpgh.common.utils import process_external_url

import urllib


def to_directions_link(location):
    daddr = ''
    if location.address:
        daddr = location.address
        if location.postcode:
            daddr += ', ' + location.postcode
    elif location.longitude and not location.latutude:
        daddr = '(%f,%f)' % (float(location.longitude), float(location.latutude))

    if not daddr:
        return None
    else:
        return 'http://maps.google.com/maps?' + urllib.urlencode({'daddr': daddr})


class PlaceFeedItem(ViewModel):
    def __init__(self, place_profile, user=None):
        super(PlaceFeedItem, self).__init__()
        self.place = place_profile.place
        # description isn't part of core Place
        self._description = place_profile.description
        # TODO: reenable favorites when user model is created
        # if user:
        #     self.is_favorite = FavoriteItem.objects.filter_by_type(model_instance=place).count() > 0

    def to_data(self):
        data = super(PlaceFeedItem, self).to_data()
        # add description to the place entry
        data['place']['description'] = self._description
        return data


class PlaceDetail(ViewModel):
    def __init__(self, place_profile, user=None):
        super(PlaceDetail, self).__init__()
        self.place = place_profile.place
        self._profile = place_profile
        # clean url for output
        self._profile.url = process_external_url(self._profile.url)

        # TODO: reenable favorites when user model is created
        # if user:
        #     self.is_favorite = FavoriteItem.objects.filter_by_type(model_instance=place).count() > 0

    def to_data(self, *args, **kwargs):
        '''Manually handles setting of place data'''
        data = super(PlaceDetail, self).to_data()
        # inject profile data into place object
        data['place'].update(self._profile.to_data())
        return data


class PlaceRelatedFeeds(FeedCollection):
    def __init__(self, place, user=None):
        # TODO: This is a temporary placeholder for related feeds. Need events, offers, etc. here,
        #  but using places for the sake of testing and mockup styling
        places1_feed = PlacesFeed.init_from_places(Place.objects.all().order_by('?')[:4], user=user)
        places2_feed = PlacesFeed.init_from_places(Place.objects.all().order_by('?')[:4], user=user)
        places3_feed = PlacesFeed.init_from_places(Place.objects.all().order_by('?')[:4], user=user)

        feed_tuples = [('Places 1', places1_feed),
                       ('Places 2', places2_feed),
                       ('Places 3', places3_feed),
                    ]
        super(PlaceRelatedFeeds, self).__init__(feed_tuples)

    def to_html(self, request=None):
        print 'PlaceRelatedFeeds:', self.__dict__
        return super(PlaceRelatedFeeds, self).to_html(request)
