from onlyinpgh.common.core.viewmodels import ViewModel

from onlyinpgh.common.viewmodels import FeedCollection
from onlyinpgh.common.utils import process_external_url

from django.contrib.auth.models import User
from onlyinpgh.events.models import Event
from onlyinpgh.events.viewmodels import EventFeedItem
from onlyinpgh.specials.models import Special
from onlyinpgh.specials.viewmodels import SpecialFeedItem

import urllib

DEFAULT_IMAGE_URL = 'http://3.bp.blogspot.com/_bX6A151GK68/SrC0hBrYTXI/AAAAAAAAAE0/FQ2ELSQIrh8/s320/cute+cat+pictures+round+cat.jpg'


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
    '''
    Exposes the following data:
        place
            id
            name
            location
                address
                postcode
                town
                state
                country
                latitude
                longitude
            image_url
            description
            [tags]
                id
                name
        is_favorite (boolean)
    '''
    def __init__(self, place, user=None):
        super(PlaceFeedItem, self).__init__()
        self.place = place
        if isinstance(user, User):
            self.is_favorite = place.favorite_set\
                                    .filter(user=user, is_favorite=True)\
                                    .count() > 0
        else:
            self.is_favorite = False

    def to_data(self, *args, **kwargs):
        data = super(PlaceFeedItem, self).to_data(*args, **kwargs)
        place_data = data.get('place')
        keepers = set(('id', 'name', 'location', 'image_url', 'description', 'tags'))
        for k in place_data.keys():
            if k not in keepers:
                place_data.pop(k)
        if not place_data['image_url']:
            place_data['image_url'] = DEFAULT_IMAGE_URL
        return data


class PlaceDetail(ViewModel):
    '''
    Exposes the following data:
        place
            id
            dtcreated
            name
            location
                address
                postcode
                town
                state
                country
                latitude
                longitude
            image_url
            description
            [tags]
                id
                name
            hours
            parking
            phone
            url
            fb_id
            twitter_username
        is_favorite (boolean)
    '''
    def __init__(self, place, user=None):
        super(PlaceDetail, self).__init__()
        self.place = place
        if isinstance(user, User):
            self.is_favorite = place.favorite_set\
                                    .filter(user=user, is_favorite=True)\
                                    .count() > 0
        else:
            self.is_favorite = False

    def to_data(self, *args, **kwargs):
        '''Manually handles setting of place data'''
        data = super(PlaceDetail, self).to_data(*args, **kwargs)
        url = data['place']['url']
        if url:
            data['place']['url'] = process_external_url(url)
        if not data['place']['image_url']:
            data['place']['image_url'] = DEFAULT_IMAGE_URL

        return data


class PlaceRelatedFeeds(FeedCollection):
    '''
        events_feed
            [EventFeedItems]
        specials_feed
            [SpecialFeedItems]
    '''
    def __init__(self, place, user=None):
        events_feed = [EventFeedItem(e, user) for e in Event.objects.filter(place=place)]
        specials_feed = [SpecialFeedItem(s, user) for s in Special.objects.filter(place=place)]
        super(PlaceRelatedFeeds, self).__init__(
            events=events_feed,
            specials=specials_feed
        )
