from django.shortcuts import render
from onlyinpgh.places.models import Place
from onlyinpgh.events.models import Event
from onlyinpgh.specials.models import Special


def home(request):
    return render(request, 'testbed/home.html')


def maps(request):
    return render(request, 'testbed/maps.html', {
        'places': [p for p in Place.listed_objects.order_by('?')[:10] if p.location and p.location.is_geocoded()],
        'events': [e for e in Event.objects.order_by('?') if e.place and e.place.location and e.place.location.is_geocoded()],
        'specials': [s for s in Special.objects.order_by('?') if s.place and s.place.location and s.place.location.is_geocoded()],
        })
