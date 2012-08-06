from scenable.events.models import Event
from scenable.specials.models import Special
from django.contrib.auth.models import User

from scenable.events.viewmodels import EventData
from scenable.specials.viewmodels import SpecialData

from scenable.common.utils import get_cached_thumbnail

from django.template.defaultfilters import truncatewords


class PlaceData(object):
    def __init__(self, place, user=None):
        fields = ('id', 'name', 'location', 'description', 'tags', 'image', 'hours',
                  'url', 'fb_id', 'twitter_username', 'listed', 'get_absolute_url')
        if isinstance(user, User):
            self.is_favorite = place.favorite_set.filter(user=user).count() > 0
        else:
            self.is_favorite = False
        for attr in fields:
            setattr(self, attr, getattr(place, attr))
        # do hours and parking separately
        #self.parking = place.parking_unpacked()
        self.pk = self.id

    def serialize(self):
        '''
        Temporary method to take the place of TastyPie serialization
        functionality. Will remove later in place of TastyPie functionality,
        but too many special issues (e.g. thumbnails) to worry about
        doing "right" at the moment.
        '''
        thumb_small = get_cached_thumbnail(self.image, 'small') if self.image else None
        thumb_standard = get_cached_thumbnail(self.image, 'standard') if self.image else None

        return {
            'name': self.name,
            'description': truncatewords(self.description, 15),
            'location': {
                'address': self.location.address,
                'latitude': float(self.location.latitude) if self.location.latitude is not None else None,
                'longitude': float(self.location.longitude) if self.location.longitude is not None else None,
                'is_gecoded': self.location.latitude is not None and self.location.longitude is not None,
            } if self.location else None,
            'tags': [{
                'name': tag.name,
                'permalink': tag.get_absolute_url(),
            } for tag in self.tags.all()[:4]],
            'hours': [{
                'days': listing.days,
                'hours': listing.hours
            } for listing in self.hours],
            'image': self.image.url if self.image else '',
            # special fields only for JSON output
            'permalink': self.get_absolute_url(),
            'thumb_small': thumb_small.url if thumb_small else '',
            'thumb_standard': thumb_standard.url if thumb_standard else '',
        }


class PlaceRelatedFeeds(object):
    def __init__(self, place, user=None):
        self.events_feed = [EventData(e, user) for e in Event.objects.filter(place=place)]
        self.specials_feed = [SpecialData(s, user) for s in Special.objects.filter(place=place)]
