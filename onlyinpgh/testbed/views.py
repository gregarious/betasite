from django.shortcuts import render
from onlyinpgh.places.models import Place
from onlyinpgh.events.models import Event
from onlyinpgh.common.utils.jsontools import json_response
import json


from onlyinpgh.testbed.api import PlaceFeedResource

def home(request):
    return render(request, 'testbed/home.html')


def maps(request):
    places = [p for p in Place.listed_objects.order_by('?') if p.location and p.location.is_geocoded()][:5]
#    places[0].name = '</script>alert()'
    rsrc = PlaceFeedResource()
    bundles = (rsrc.build_bundle(request=request, obj=obj) for obj in places)
    dehydrated = [rsrc.full_dehydrate(bundle) for bundle in bundles]

    return render(request, 'testbed/maps.html', {
        'places': places,
        'places_json': rsrc.serialize(None, dehydrated, 'application/json'),
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
