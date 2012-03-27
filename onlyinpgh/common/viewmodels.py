from onlyinpgh.common.core.viewmodels import ViewModel


class FeedCollection(ViewModel):
    def __init__(self, **kwargs):
        '''
        kwargs should be a list of feed item lists. The key names
        in this constructor will become the keys of the data.
        '''
        super(FeedCollection, self).__init__()
        for key, items in kwargs.items():
            setattr(self, key, items)


from onlyinpgh.places.models import Place
from onlyinpgh.places.viewmodels import PlaceFeedItem
from onlyinpgh.events.models import Event
from onlyinpgh.events.viewmodels import EventFeedItem
from onlyinpgh.specials.models import Special
from onlyinpgh.specials.viewmodels import SpecialFeedItem


class HotFeedCollection(FeedCollection):
    def __init__(self, user=None):
        super(HotFeedCollection, self).__init__(
            events=[EventFeedItem(e, user) for e in Event.objects.all().order_by('?')[:3]],
            places=[PlaceFeedItem(p, user) for p in Place.objects.all().order_by('?')[:3]],
            specials=[SpecialFeedItem(s, user) for s in Special.objects.all().order_by('?')[:3]]
        )
