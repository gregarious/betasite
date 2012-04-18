from django.template import Context

from django.contrib.auth.models import User
from onlyinpgh.events.models import Event
from onlyinpgh.events.contexts import EventContext
from onlyinpgh.specials.models import Special
from onlyinpgh.specials.contexts import SpecialContext


class PlaceContext(Context):
    '''
    Exposes the following data:
        place (Place model instance)
        is_favorite (boolean)
    '''
    def __init__(self, place, user=None, **kwargs):
        if isinstance(user, User):
            is_favorite = place.favorite_set\
                                    .filter(user=user, is_favorite=True)\
                                    .count() > 0
        else:
            is_favorite = False

        super(PlaceContext, self).__init__(dict(
                place=place,
                is_favorite=is_favorite),
            **kwargs)


class PlaceRelatedFeeds(Context):
    '''
        events_feed
            [EventContexts]
        specials_feed
            [SpecialContexts]
    '''
    def __init__(self, place, user=None, **kwargs):
        efeed = [EventContext(e, user) for e in Event.objects.filter(place=place)]
        sfeed = [SpecialContext(s, user) for s in Special.objects.filter(place=place)]
        super(PlaceRelatedFeeds, self).__init__(dict(
                events_feed=efeed,
                specials_feed=sfeed),
            **kwargs)
