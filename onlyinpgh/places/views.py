from django.shortcuts import get_object_or_404, render_to_response
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from onlyinpgh.common.utils.jsontools import serialize_resources, jsonp_response
from onlyinpgh.common.views import PageContext

from onlyinpgh.places.models import Place
from onlyinpgh.places.resources import PlaceFeedResource
from onlyinpgh.places.viewmodels import PlaceData, PlaceRelatedFeeds


def page_feed(request):
    '''
    View function that handles a page load request for a feed of place
    items.

    Returns page response with main_content set as:
        items: list of PlaceContext items
        prev_p: number of previous page places (if applicable)
        next_p: number of next page of places (if applicable)
    '''
    all_places = Place.listed_objects.all()
    paginator = Paginator(all_places, 10)
    p = request.GET.get('p')
    try:
        page = paginator.page(p)
    except PageNotAnInteger:
        page = paginator.page(1)
    except EmptyPage:
        page = paginator.page(paginator.num_pages)

    places = page.object_list
    items = [PlaceData(place, user=request.user) for place in places]
    # need the items in json form for bootstrapping to BB models
    items_json = serialize_resources(PlaceFeedResource(), items)

    content = {'items': items,
               'items_json': items_json,
               'prev_p': page.previous_page_number() if page.has_previous() else None,
               'next_p': page.next_page_number() if page.has_next() else None}

    page_context = PageContext(request,
        current_section='places',
        page_title='Scenable | Oakland Places',
        content_dict=content)
    return render_to_response('places/page_feed.html', page_context)


def page_details(request, pid):
    '''
    Returns page response with main content set as:
        place (PlaceContext object)
        related_feeds (PlaceRelatedFeeds object)
    '''
    action = request.GET.get('action')
    if action:
        raise NotImplementedError
    #     # handle the action and get a dict with details about the result
    #     result = _handle_place_action(request, pid, action)
    #     # if the request was made via AJAX, client just expects the result dict returned as JSON
    #     if request.is_ajax():
    #         return package_json_response(result)
    # # TODO: return error message on action failure?

    # build and render place detail viewmodel
    place = get_object_or_404(Place, id=pid)
    details = PlaceData(place, user=request.user)

    # build related feeds viewmodel
    related_feeds = PlaceRelatedFeeds(place, user=request.user)

    content = dict(
        place=details,
        related_feeds=related_feeds)
    page_context = PageContext(request,
        current_section='places',
        page_title='Scenable | %s' % place.name,
        content_dict=content)

    return render_to_response('places/page_place.html', page_context)


@jsonp_response
def feed_app(request):
    return []


@jsonp_response
def detail_app(request, pid):
    return {}
