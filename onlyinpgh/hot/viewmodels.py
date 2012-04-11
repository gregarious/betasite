from onlyinpgh.common.viewmodels import FeedCollection

from onlyinpgh.places.models import Place
from onlyinpgh.places.viewmodels import PlaceFeedItem
from onlyinpgh.events.models import Event
from onlyinpgh.events.viewmodels import EventFeedItem
from onlyinpgh.specials.models import Special
from onlyinpgh.specials.viewmodels import SpecialFeedItem


class HotFeedCollection(FeedCollection):
    def __init__(self, user=None):
        super(HotFeedCollection, self).__init__(
            events=[EventFeedItem(e, user) for e in Event.listed_objects.all().order_by('?')[:3]],
            places=[PlaceFeedItem(p, user) for p in Place.listed_objects.all().order_by('?')[:3]],
            specials=[SpecialFeedItem(s, user) for s in Special.objects.all().order_by('?')[:3]]
        )
