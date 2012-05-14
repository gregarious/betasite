from scenable.places.models import Place
from scenable.places.viewmodels import PlaceData
from scenable.events.models import Event
from scenable.events.viewmodels import EventData
from scenable.specials.models import Special
from scenable.specials.viewmodels import SpecialData


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