from onlyinpgh.places.models import Place
from onlyinpgh.places.viewmodels import PlaceData
from onlyinpgh.events.models import Event
from onlyinpgh.events.viewmodels import EventData
from onlyinpgh.specials.models import Special
from onlyinpgh.specials.viewmodels import SpecialData


class NowFeedItem(object):
    def __init__(self, instance):
        if isinstance(instance, Place):
            self.model = 'Place'
            self.instance = PlaceData(instance)
        elif isinstance(instance, Event):
            self.model = 'Event'
            self.instance = EventData(instance)
        elif isinstance(instance, Special):
            self.model = 'Special'
            self.instance = SpecialData(instance)
        else:
            self.model = ''
            self.instance = instance
