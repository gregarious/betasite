from django.shortcuts import render, get_object_or_404

from onlyinpgh.common.utils.jsontools import jsonp_response, package_json_response
from onlyinpgh.common.core.rendering import render_viewmodel, render_viewmodels_as_ul

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


def feed_page(request):
    '''
    View function that handles a page load request for a feed of place
    items.

    Renders page.html with main_content set to the rendered HTML of
    a feed.
    '''
    # get a list of rendered items
    places = Place.objects.all()[:10]
    items = [PlaceFeedItem(place, user=request.user) for place in places]
    content = render_viewmodels_as_ul(items, 'places/feed_item.html', container_class_label='places feed')
    return render(request, 'page.html', {'main_content': content})


def detail_page(request, pid):
    '''
    View displays single places.
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
    place = get_object_or_404(Place,id=pid)
    details = PlaceDetail(place, user=request.user)
    content = render_viewmodel(details,
                template='places/single.html',
                class_label='place-single')

    # build and render related feeds viewmodel
    # related_feeds = PlaceRelatedFeeds(place, user=request.user)
    # content += related_feeds.to_html(request)

    # as long as there was no AJAX-requested action, we will return a fully rendered new page
    return render(request, 'page.html', {'main_content': content})


@jsonp_response
def feed_app(request):
    places = Place.objects.all()[:10]
    feed_items = [PlaceFeedItem(place, user=request.user) for place in places]
    return [item.to_data() for item in feed_items]


@jsonp_response
def detail_app(request, pid):
    place = Place.objects.get(place__id=pid)
    details = PlaceDetail(place, user=request.user)
    return details.to_data()    # decorator will handle JSON response wrapper


@jsonp_response
def place_lookup(request):
    if request.GET:
        results = Place.objects.filter(name__icontains=request.GET.get('q', ''))
        limit = request.GET.get('limit')
        if limit:
            results = results[:limit]

    return [{'id':p.id, 'name':p.name} for p in results]
