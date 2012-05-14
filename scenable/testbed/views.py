from django.shortcuts import render
from scenable.places.models import Place
from scenable.events.models import Event
from scenable.common.utils.jsontools import json_response, serialize_resources
import json


from scenable.places.resources import PlaceFeedResource
from scenable.places.viewmodels import PlaceData


def home(request):
    return render(request, 'testbed/home.html')


def maps(request):
    places = [PlaceData(p) for p in Place.listed_objects.order_by('?') if p.location and p.location.is_geocoded()][:5]
    return render(request, 'testbed/maps.html', {
        'places': places,
        'places_json': serialize_resources(PlaceFeedResource(), places, request)
    })


def pipe(request):
    return render(request, 'testbed/pipe.html')


@json_response
def ajax_newplace(request):
    p = Place.objects.exclude(location=None).order_by('?')[0]
    return {
        'name': p.name,
        'location': {
            'address': p.location.address,
            'latitude': str(p.location.latitude),
            'longitude': str(p.location.longitude)
        },
    }


@json_response
def ajax_newevent(request):
    e = Event.objects.exclude(place=None).order_by('?')[0]
    return {
        'name': e.name,
        'place': {
            'location': {
                'address': e.place.location.address,
                'latitude': str(e.place.location.latitude),
                'longitude': str(e.place.location.longitude)
            } if e.place.location else {},
        },
    }