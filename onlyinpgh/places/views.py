from django.shortcuts import render
from django.template import Context
from django.template.loader import get_template
from django.utils.safestring import SafeUnicode
from onlyinpgh.common.utils.jsontools import json_response, jsonp_response, package_json_response

from onlyinpgh.places.models import Place
from onlyinpgh.identity.models import FavoriteItem
from onlyinpgh.places.viewmodels import PlacesFeed, PlaceDetail, PlaceRelatedFeeds

# for feed collection building

from datetime import datetime, timedelta
import urllib
from time import sleep

def _places_all():
    return Place.objects.select_related().all()[:10]

def _get_checkin_cutoff():
    return datetime.utcnow() - timedelta(hours=3)

def _handle_place_action(request,pid,action):
    '''
    Returns a status dict that resulted from the action.
    '''
    failure = lambda msg: {'status': 'error', 'msg': msg}
    success = lambda msg: {'status': 'success', 'msg': msg}
    if not request.user.is_authenticated():
        return failure('user not authenticated')
    elif not request.user.is_authenticated():
        return failure('user account inactive')
    else:
        try:
            place = Place.objects.get(id=pid)
        except Place.DoesNotExist:
            return failure('invalid place id')

        if action == 'addfav' or action == 'removefav':
            existing = FavoriteItem.objects.filter_by_type(model_type=Place,
                            model_instance=place,
                            user=request.user)
            if action == 'addfav':
                if len(existing) > 0:
                    # despite non-action, we count this as a success
                    return success('item already in favorites')
                else:
                    FavoriteItem.objects.create(user=request.user,
                                                content_object=place)
                    return success('added')
            elif action == 'removefav':
                if len(existing) > 0:
                    existing.delete()
                    return success('removed')
                else:
                    # despite non-action, we count this as a success
                    return success('item not in favorites')
        else:
            return failure('invalid action')

def feed_page(request):
    '''
    View function that handles a page load request for a feed of place
    items. 

    Renders page.html with main_content set to the rendered HTML of
    a feed.
    '''
    feed = PlacesFeed.init_from_places(_places_all(),user=request.user)

    return render(request,'page.html',
                    {'main_content':feed.to_html(request)})

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

    # build and render place detail viewmodel
    place = Place.objects.select_related().get(id=pid)
    details = PlaceDetail(place,user=request.user)
    html = details.to_html(request)

    html += SafeUnicode(u'\n<hr/><hr/>\n')

    # build and render related feeds viewmodel
    related_feeds = PlaceRelatedFeeds(place,user=request.user)
    html += related_feeds.to_html(request)

    # as long as there was no AJAX-requested action, we will return a fully rendered new page 
    return render(request,'page.html',
            Context({'main_content':html}))

## APP VIEW FUNCTIONS CURRENTLY BROKEN ##
@jsonp_response
def feed_app(request):
    feed = PlacesFeed.init_from_places(_places_all(),user=request.user)
    return feed.to_data()   # decorator will handle JSON response wrapper

@jsonp_response
def detail_app(request,pid):
    place = Place.objects.select_related().get(id=pid)
    details = PlaceDetail(place,user=request.user)
    return details.to_data()    # decorator will handle JSON response wrapper