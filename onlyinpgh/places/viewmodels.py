from onlyinpgh.events.models import Event
from onlyinpgh.specials.models import Special
from django.contrib.auth.models import User

from onlyinpgh.events.viewmodels import EventData
from onlyinpgh.specials.viewmodels import SpecialData


class PlaceData(object):
    def __init__(self, place, user=None):
        fields = ('id', 'name', 'location', 'description', 'tags', 'image',
                  'hours', 'parking', 'url', 'fb_id', 'twitter_username',
                  'listed')
        if isinstance(user, User):
            self.is_favorite = place.favorite_set\
                                    .filter(user=user, is_favorite=True)\
                                    .count() > 0
        else:
            self.is_favorite = False
        for attr in fields:
            setattr(self, attr, getattr(place, attr))


class PlaceRelatedFeeds(object):
    def __init__(self, place, user=None):
        self.events_feed = [EventData(e, user) for e in Event.objects.filter(place=place)]
        self.specials_feed = [SpecialData(s, user) for s in Special.objects.filter(place=place)]
