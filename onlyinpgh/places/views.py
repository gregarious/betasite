from django.http import HttpResponse
from django.shortcuts import render, render_to_response

from django.template import Context, RequestContext

from onlyinpgh.places.models import Place, Meta as PlaceMeta, Checkin as PlaceCheckin
from onlyinpgh.identity.models import FavoriteItem

from onlyinpgh.utils.jsontools import json_response, jsonp_response, package_json_response
from onlyinpgh.utils import ViewInstance, SelfRenderingView

from datetime import datetime, timedelta

class PlaceView(ViewInstance):
    def __init__(self,place):
        super(PlaceView,self).__init__(place,extract_m2m=True)

        self.phone = place.get_meta('phone')
        self.url = place.get_meta('url')
        self.hours = place.get_meta('hours')
        self.image_url = place.get_meta('image_url')

class FeedItem(SelfRenderingView):
    template_name = 'places/feed_item.html'
    
    def __init__(self,place,user=None):
        self.place = PlaceView(place)   # adds meta info, extracts tags from m2m manager
        self.user = user
        if self.user:
            self.is_favorite = FavoriteItem.objects.filter(user=self.user,
                                                            object_id=self.place.id)\
                                                    .count() > 0
        # temporary placeholder
        if not self.place.image_url:
            self.place.image_url = 'http://www.nasm.si.edu/images/collections/media/thumbnails/DefaultThumbnail.gif'

    def to_app_data(self):
        tag_data = [{'name':t.name,'id':t.id} for t in self.place.tags]
        data = { 'place': {
                    'id':       self.place.id,
                    'name':     self.place.name,
                    'description':  self.place.description,
                    'image_url':    self.place.image_url,
                    'tags':     tag_data,
                    'hours':    self.place.hours,
                    'url':      self.place.url,
                },
            }

        if self.location:
            data['location'] = {
                    'address':      self.location.address,
                    'longitude':    float(self.location.longitude),
                    'latitude':     float(self.location.latitude),
                }
        return data

# class PlaceView(ViewInstance):
#     def __init__(self,place):
#         super(ViewPlace,self).__init__(place,extract_m2m=True)

#         self.phone = place.get_meta('phone')
#         self.url = place.get_meta('url')
#         self.hours = place.get_meta('hours')
#         self.image_url = place.get_meta('image_url')

    # # TODO: move this outside. send in user-specific stuff as a seperate object
    # def add_userdata(self,user):
    #     '''
    #     Appends 'checkin' and 'favorite' members to this ViewPlace
    #     '''
    #     try:
    #         self.checkin = PlaceCheckin.objects.filter(place=self._orig_instance,
    #                                                     user=user,
    #                                                     dtcreated__gt=_get_checkin_cutoff()) \
    #                                                 .order_by('-dtcreated')[0]
    #     except IndexError:
    #         self.checkin = None

    # def to_app_data(self):
    #     tag_data = [{'name':t.name,'id':t.id} for t in self.tags]
    #     data = {
    #         'id':       self.id,
    #         'name':     self.name,
    #         'description':  self.description,
    #         'image_url':    self.image_url,
    #         'tags':     tag_data,
    #         'hours':    self.hours,
    #         'url':      self.url,
    #         }

    #     if self.location:
    #         data['location'] = {
    #                 'address':      self.location.address,
    #                 'longitude':    float(self.location.longitude),
    #                 'latitude':     float(self.location.latitude),
    #             },
    #     return data

def _view_data_all():
    return [ViewPlace(p) for p in Place.objects.select_related().all()[:10]]

def _view_data_id(pid,user):
    place = ViewPlace(Place.objects.select_related().get(id=pid))
    place.add_userdata(user)
    print dir(place)
    return place

def _get_checkin_cutoff():
    return datetime.utcnow() - timedelta(hours=3)

def _handle_place_action(request,pid,action):
    '''
    Returns a status dict that resulted from the action.
    '''
    failresp = lambda msg: {'status': 'failure', 'error': msg}
    if not request.user.is_authenticated():
        return failresp('user not authenticated')
    elif not request.user.is_authenticated():
        return failresp('user account inactive')
    else:
        try:
            place = Place.objects.get(id=pid)
        except Place.DoesNotExist:
            return failresp('invalid place id')

        if action == 'checkin':
            print PlaceCheckin.objects.filter(place__id=pid,
                                            user=request.user)
            # don't allow multiple checkins within 3 hours
            if PlaceCheckin.objects.filter(place__id=pid,
                                            user=request.user,
                                            dtcreated__gt=_get_checkin_cutoff()).count() > 0:
                return failresp('already checked in')
            else:
                PlaceCheckin.objects.create(place=place,
                                            user=request.user)
        elif action == 'favorite':
            FavoriteItem.objects.create(content_object=place,
                                        user=request.user)
        else:
            return failresp('invalid action')
    return {'status': 'success'}

def feed_page(request):
    data = {'places':   _view_data_all()}
    # each feed item needs a link to the details page
    return render(request,
                    'places/places_feed.html',
                    data)

def detail_page(request,pid):
    '''
    View displays single places as well as handling many user actions taken
    on these places.

    The actions are specified via an 'action' GET argument. If the GET request
    is an XMLHttpRequest (ajax), the response will be a JSON object noting the
    status of the request. If no action or a non-AJAX request, the whole page
    will be returned.

    Supported actions:
    - checkin: User check in to the given place
    - favorite: User favorites the given place
    '''
    action = request.GET.get('action')

    # handle the action and get a dict with details about the result
    result = _handle_place_action(request,pid,action)
    # if the request was made via AJAX, client just expects the result dict returned as JSON
    if request.is_ajax():
        return package_json_response(result)

    # as long as there was no AJAX-requested action, we will return a fully rendered new page 
    data = {'places':   _view_data_id(pid,request.user)}
    return render(request,
                    'places/places_single.html',
                    data)

@jsonp_response
def feed_app(request):
    data = {'places':   [vp.to_app_data() for vp in _view_data_all()]}
    return data

@jsonp_response
def detail_app(request,pid):
    data = {'place':    _view_data_id(pid).to_app_data()}
    return data
