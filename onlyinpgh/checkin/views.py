from django.http import HttpResponse
from onlyinpgh.utils.jsontools import json_response, jsonp_response

from onlyinpgh.places.models import Place
from onlyinpgh.events.models import Event
from onlyinpgh.checkin.models import PlaceCheckin, EventCheckin

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