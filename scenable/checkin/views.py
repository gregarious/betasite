from django.http import HttpResponse
from scenable.common.utils.jsontools import json_response, jsonp_response

from scenable.places.models import Place
from scenable.events.models import Event
from scenable.checkin.models import PlaceCheckin, EventCheckin

@json_response
def place_checkin(request,pid):
    if not request.user.is_authenticated():
        err = 'user not authenticated'
    elif not request.user.is_authenticated():
        err = 'user account inactive'
    else:
        try:
            PlaceCheckin.objects.create(place=Place.objects.get(id=pid),
                                        user=request.user)
            return {'status': 'success'}
        except Place.DoesNotExist:
            err = 'invalid place id'
    return {'status': 'failure', 'error': 'invalid place id'}