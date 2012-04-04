from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator, EmptyPage, InvalidPage

from onlyinpgh.common.utils.jsontools import jsonp_response, package_json_response
from onlyinpgh.common.core.rendering import render_viewmodel, render_safe
from onlyinpgh.common.views import page_response, render_main

from onlyinpgh.places.models import Place
from onlyinpgh.places.viewmodels import PlaceFeedItem, PlaceDetail, PlaceRelatedFeeds

from datetime import datetime, timedelta


def _get_checkin_cutoff():
    return datetime.utcnow() - timedelta(hours=3)


def _handle_place_action(request, pid, action):
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


def page_feed(request):
    '''
    View function that handles a page load request for a feed of place
    items.

    Returns page response with main content set to the feed.
    '''
    all_places = Place.listed_objects.all()
    paginator = Paginator(all_places, 10)
    try:
        page_num = int(request.GET.get('p', '1'))
    except ValueError:
        page_num = 1

    try:
        page = paginator.page(page_num)
    except (EmptyPage, InvalidPage):
        page = paginator.page(paginator.num_pages)

    items = [PlaceFeedItem(place, user=request.user) for place in page.object_list]

    main = render_main(render_safe('places/main_feed.html',
        items=items,
        prev_p=page.previous_page_number() if page.has_previous() else None,
        next_p=page.next_page_number() if page.has_next() else None))

    return page_response(main, request)


def page_details(request, pid):
    '''
    Returns page response with main content set to the details.
    '''
    action = request.GET.get('action')
    if action:
        # handle the action and get a dict with details about the result
        result = _handle_place_action(request, pid, action)
        # if the request was made via AJAX, client just expects the result dict returned as JSON
        if request.is_ajax():
            return package_json_response(result)
    # TODO: return error message on action failure?

    # build and render place detail viewmodel
    place = get_object_or_404(Place, id=pid)
    details = PlaceDetail(place, user=request.user)

    # build related feeds viewmodel
    related_feeds = PlaceRelatedFeeds(place, user=request.user)

    # as long as there was no AJAX-requested action, we will return a fully rendered new page
    main = render_main(render_safe('places/main_place.html',
                            place_detail=details,
                            related_feeds=related_feeds))
    return page_response(main, request)


@jsonp_response
def feed_app(request):
    places = Place.list_objects.all()[:10]
    feed_items = [PlaceFeedItem(place, user=request.user) for place in places]
    return [item.to_data() for item in feed_items]


@jsonp_response
def detail_app(request, pid):
    place = Place.listed_objects.get(place__id=pid)
    details = PlaceDetail(place, user=request.user)
    return details.to_data()    # decorator will handle JSON response wrapper


@jsonp_response
def place_lookup(request):
    if request.GET:
        results = Place.listed_objects.filter(name__icontains=request.GET.get('q', ''))
        limit = request.GET.get('limit')
        if limit:
            results = results[:limit]

    return [{'id':p.id, 'name':p.name} for p in results]
