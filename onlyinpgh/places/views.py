from django.http import HttpResponse
from django.shortcuts import render, render_to_response

from django.template import Context, RequestContext
from django.template.loader import get_template

from onlyinpgh.places.models import Place, Meta as PlaceMeta, Checkin as PlaceCheckin
from onlyinpgh.identity.models import FavoriteItem
from onlyinpgh.offers.models import Offer

from onlyinpgh.utils.jsontools import json_response, jsonp_response, package_json_response
from onlyinpgh.utils import ViewInstance, SelfRenderingView, process_external_url

from datetime import datetime, timedelta
import urllib

def to_directions_link(location):
    daddr = ''
    if location.address:
        daddr = location.address
        if location.postcode:
            daddr += ', ' + location.postcode
    elif location.longitude and not location.latutude:
        daddr = '(%f,%f)' % (float(location.longitude),float(location.latutude))

    if not daddr:
        return None
    else:
        return 'http://maps.google.com/maps?' + urllib.urlencode({'daddr':daddr})

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
        self.place = place
        # explicitly grab the image url and tags to make them context-friendly
        self.place.image_url = place.get_meta('image_url')

        if user:
            self.is_favorite = FavoriteItem.objects.filter_by_type(model_type=Place,
                                                                    model_instance=self.place)\
                                                                .count() > 0
        # temporary placeholder
        if not self.place.image_url:
            self.place.image_url = 'http://www.nasm.si.edu/images/collections/media/thumbnails/DefaultThumbnail.gif'

    def to_app_data(self):
        '''
        Handles explicit conversion of the FeedItem to serialized data
        along with any string formatting operations (e.g. date formatting)
        '''
        loc_data = None
        if self.place.location:
            loc_data = {
                'address':      self.place.location.address,
                'longitude':    float(self.place.location.longitude),
                'latitude':     float(self.place.location.latitude),
            }

        data = { 'place': {
                    'id':       self.place.id,
                    'name':     self.place.name,
                    'image_url':    self.place.image_url,
                    'tags':     [{'name':t.name,'id':t.id} for t in self.place.tags.all()],
                    'location': loc_data,
                },
            }

        return data

class SingleItem(FeedItem):
    template_name = 'places/single.html'

    def __init__(self,place,user=None):
        # super will handle place (with image_url and tags) and is_favorite
        super(SingleItem,self).__init__(place,user=user)
        self.place.hours = place.get_meta('hours')
        self.place.url = place.get_meta('url')
        if self.place.url:
            self.place.url = process_external_url(self.place.url)

        specials = Offer.objects.filter(place=self.place)
        if specials:
            self.featured_special = specials[0] # arbitrary choice
        if self.place.location:
            self.directions_link = to_directions_link(place.location)

    def to_app_data(self):
        # get super's app data first, then insert new fields
        data = super(SingleItem,self).to_app_data()
        data['place'].update(
            { 'hours': self.place.hours,
              'url':   self.place.url })
        data.update(
            { 'featured_special': {   
                    'description': self.featured_special.description,
                    'point_value': self.featured_special.point_value, 
                    'id':          self.featured_special.id},
              'directions_link':    self.directions_link })
        return data

class RelatedFeeds(SelfRenderingView):
    template_name = 'feed_collection.html'

    def __init__(self,place,user=None):
        self.place = place
        # TODO: MORE

def _feed_items_all(user=None):
    return [FeedItem(p,user) for p in Place.objects.select_related().all()[:10]]

def _single_id(pid,user=None):
    return SingleItem(Place.objects.select_related().get(id=pid),
                        user=user)

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

        if action == 'fav' or action == 'unfav':
            existing = FavoriteItem.objects.filter_by_type(model_type=Place,
                            model_instance=place,
                            user=request.user)
            if action == 'fav':
                if len(existing) > 0:
                    return failresp('item already in favorites')
                else:
                    FavoriteItem.objects.create(user=request.user,
                                                content_object=place)
            elif action == 'unfav':
                if len(existing) > 0:
                    existing.delete()
                else:
                    return failresp('item not in favorites')
        else:
            return failresp('invalid action')
    return {'status': 'success'}

def feed_page(request):
    '''
    View function that handles a page load request for a feed of place
    items. 

    Renders page.html with main_content set to the rendered HTML of
    a feed.
    '''
    # get a list of rendered Place FeedItems
    items = _feed_items_all(request.user)
    rendered_items = [item.self_render() for item in items]

    # feed these rendered blocks into feed.html
    feed_context = Context(dict(items=rendered_items,
                                class_name='place_feed'))
    feed_html = get_template('feed.html').render(feed_context)

    return render(request,'page.html',
                    {'main_content':feed_html})

def detail_page(request,pid):
    '''
    View displays single places as well as handling many user actions taken
    on these places.

    The actions are specified via an 'action' GET argument. If the GET request
    is an XMLHttpRequest (ajax), the response will be a JSON object noting the
    status of the request. If no action or a non-AJAX request, the whole page
    will be returned.

    Supported actions:
    - fav: User adds given place to his favorites
    - unfav: User removes given place from favorites
    '''
    action = request.GET.get('action')
    if action:
        # handle the action and get a dict with details about the result
        result = _handle_place_action(request,pid,action)
        # if the request was made via AJAX, client just expects the result dict returned as JSON
        if request.is_ajax():
            return package_json_response(result)

    # TODO: return error message on action failure?
    detail_view = _single_id(pid,user=request.user)

    # as long as there was no AJAX-requested action, we will return a fully rendered new page 
    return render(request,'page.html',
                    Context({'main_content':detail_view.self_render()}))

## APP VIEW FUNCTIONS CURRENTLY BROKEN ##
@jsonp_response
def feed_app(request):
    items = _feed_items_all(request.user)
    return [item.to_app_data() for item in items]

@jsonp_response
def detail_app(request,pid):
    return _single_id(pid,user=request.user).to_app_data()