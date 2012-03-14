from onlyinpgh.common.core.viewmodels import ViewModel

from onlyinpgh.places.models import Place
from onlyinpgh.identity.models import FavoriteItem

from onlyinpgh.common.viewmodels import FeedCollection
from onlyinpgh.tags.viewmodels import TagList

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


def location_to_data(location):
    '''Helper for ViewModels that need a subset of Location data'''
    return {
        'address':      location.address,
        'longitude':    float(location.longitude) if location.longitude else None,
        'latitude':     float(location.latitude) if location.latitude else None,
    }


def place_to_data(place, place_meta):
    '''Helper for ViewModels that need a subset of Place data'''
    data = {
        'id':       place.id,
        'name':     place.name,
        'location': location_to_data(place.location) if place.location else None,
        'directions_link': to_directions_link(place.location),
    }
    data.update(place_meta)
    return data


class PlaceFeedItem(ViewModel):
    def __init__(self, place, user=None):
        super(PlaceFeedItem, self).__init__()
        self._place = place
        # FeedItems only need the image_url
        self._meta = {
            'image_url': place.get_meta('image_url')
        }
        # temporary placeholder
        if not self._meta['image_url']:
            self._meta['image_url'] = 'http://www.nasm.si.edu/images/collections/media/thumbnails/DefaultThumbnail.gif'

        self.tag_list = TagList(place.tags.all())
        if user:
            self.is_favorite = FavoriteItem.objects.filter_by_type(model_instance=place).count() > 0

    def to_data(self, *args, **kwargs):
        '''Manually handles setting of place data'''
        cleaned_dict = super(PlaceFeedItem, self).to_data(*args, **kwargs)
        cleaned_dict['place'] = place_to_data(self._place, self._meta)
        return cleaned_dict


class PlaceDetail(ViewModel):
    def __init__(self, place, user=None):
        super(PlaceDetail, self).__init__()
        self._place = place
        self._meta = dict([(key, place.get_meta(key))
                        for key in ('image_url', 'hours', 'phone', 'url')])

        if 'url' in self._meta:
            self._meta['url'] = process_external_url(self._meta['url'])

        # temporary placeholder
        if not self._meta['image_url']:
            self._meta['image_url'] = 'http://www.nasm.si.edu/images/collections/media/thumbnails/DefaultThumbnail.gif'

        self.tag_list = TagList(place.tags.all())
        if user:
            self.is_favorite = FavoriteItem.objects.filter_by_type(model_instance=place).count() > 0

    def to_data(self, *args, **kwargs):
        '''Manually handles setting of place data'''
        cleaned_dict = super(PlaceDetail, self).to_data(*args, **kwargs)
        cleaned_dict['place'] = place_to_data(self._place, self._meta)
        return cleaned_dict


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
