from django.http import HttpResponse
from django.shortcuts import render_to_response
from onlyinpgh.places.models import Place, Meta as PlaceMeta

from onlyinpgh.utils.decorators import jsonp_response

# TODO: there must obviously be a better way to do this. Works for now
class PlaceForTemplate:
    def __init__(self,place,url='',phone=''):
        self.phone = phone
        self.id = place.id
        self.url = url
        self.owner = place.owner
        self.description = place.description
        self.name = place.name
        self.location = place.location

def _package_place(place):
    p = PlaceForTemplate(place)
    urls = place.meta_set.filter(meta_key='url')
    if urls and urls[0].meta_value:
        p.url = urls[0].meta_value
    phone_numbers = place.meta_set.filter(meta_key='phone')
    if phone_numbers and phone_numbers[0].meta_value:
        p.phone = phone_numbers[0].meta_value
    image_url = place.meta_set.filter(meta_key='image_url')
    if image_url and image_url[0].meta_value:
        p.image_url = image_url[0].meta_value
    return p

def places_page(request):
    variables = { 'places': [_package_place(p) for p in Place.objects.all()] }
    return render_to_response('places/places_page.html',variables)

def single_place_page(request, id):
    variables = { 'p' : _package_place(Place.objects.get(id=id)) }
    return render_to_response('places/places_single.html', variables)

@jsonp_response
def ajax_places_feed(request):
    places = []
    for p in Place.objects.all()[:10]:
        place = {   'id':   p.id,
                    'name': p.name,
                    'tags': [{'name':item.tag.name} for item in p.tags.all() if item.tag.name != 'establishment'] }
        loc = p.location
        if loc:
            place['address'] = loc.address
            place['latitude'] = float(loc.latitude) if loc.latitude else None
            place['longitude'] = float(loc.longitude) if loc.longitude else None
        places.append(place)

    return {'places':places}    # decorator will handle JSONP details

@jsonp_response
def ajax_place_item(request,pid):
    p = Place.objects.get(id=pid)
    place = {   'id':   p.id,
                'name': p.name,
                'tags': [{'name':item.tag.name} for item in p.tags.all() if item.tag.name != 'establishment'] }
    loc = p.location
    if loc:
        place['address'] = loc.address
        place['latitude'] = float(loc.latitude) if loc.latitude else None
        place['longitude'] = float(loc.longitude) if loc.longitude else None

    return {'place':place}