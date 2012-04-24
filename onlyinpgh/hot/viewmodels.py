from onlyinpgh.places.models import Place
from onlyinpgh.places.viewmodels import PlaceData
from onlyinpgh.events.models import Event
from onlyinpgh.events.viewmodels import EventData
from onlyinpgh.specials.models import Special
from onlyinpgh.specials.viewmodels import SpecialData


class HotFeedCollection(object):
    def __init__(self, user=None):
        self.events = [EventData(e, user) for e in Event.listed_objects.all().order_by('?')[:3]]
        self.places = [PlaceData(p, user) for p in Place.listed_objects.all().order_by('?')[:3]]
        self.specials = [SpecialData(s, user) for s in Special.objects.all().order_by('?')[:3]]
