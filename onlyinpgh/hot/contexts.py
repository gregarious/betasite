from django.template import Context

from onlyinpgh.places.models import Place
from onlyinpgh.places.viewmodels import PlaceFeedItem
from onlyinpgh.events.models import Event
from onlyinpgh.events.viewmodels import EventFeedItem
from onlyinpgh.specials.models import Special
from onlyinpgh.specials.viewmodels import SpecialFeedItem


class HotFeedCollection(Context):
    def __init__(self, user=None, **kwargs):
        efeed = [EventFeedItem(e, user) for e in Event.listed_objects.all().order_by('?')[:3]]
        pfeed = [PlaceFeedItem(p, user) for p in Place.listed_objects.all().order_by('?')[:3]]
        sfeed = [SpecialFeedItem(s, user) for s in Special.objects.all().order_by('?')[:3]]
        super(HotFeedCollection, self).__init__(dict(
                events=efeed,
                places=pfeed,
                specials=sfeed),
            **kwargs)
