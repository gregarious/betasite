from django.template import Context

from onlyinpgh.places.models import Place
from onlyinpgh.places.contexts import PlaceContext
from onlyinpgh.events.models import Event
from onlyinpgh.events.contexts import EventContext
from onlyinpgh.specials.models import Special
from onlyinpgh.specials.contexts import SpecialContext


class HotFeedCollection(Context):
    def __init__(self, user=None, **kwargs):
        efeed = [EventContext(e, user) for e in Event.listed_objects.all().order_by('?')[:3]]
        pfeed = [PlaceContext(p, user) for p in Place.listed_objects.all().order_by('?')[:3]]
        sfeed = [SpecialContext(s, user) for s in Special.objects.all().order_by('?')[:3]]
        super(HotFeedCollection, self).__init__(dict(
                events=efeed,
                places=pfeed,
                specials=sfeed),
            **kwargs)
