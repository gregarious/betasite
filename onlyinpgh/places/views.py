from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator, EmptyPage, InvalidPage

from onlyinpgh.common.utils.jsontools import jsonp_response
from onlyinpgh.common.views import render_page
from onlyinpgh.common.contexts import PageContext

from onlyinpgh.places.models import Place
from onlyinpgh.places.contexts import PlaceContext, PlaceRelatedFeeds

# from datetime import datetime, timedelta


# def _get_checkin_cutoff():
#     return datetime.utcnow() - timedelta(hours=3)


# def _handle_place_action(request, pid, action):
#     '''
#     Returns a status dict that resulted from the action.
#     '''
#     failure = lambda msg: {'status': 'error', 'msg': msg}
#     success = lambda msg: {'status': 'success', 'msg': msg}
#     if not request.user.is_authenticated():
#         return failure('user not authenticated')
#     elif not request.user.is_authenticated():
#         return failure('user account inactive')
#     else:
#         try:
#             place = Place.objects.get(id=pid)
#         except Place.DoesNotExist:
#             return failure('invalid place id')

#         if action == 'addfav' or action == 'removefav':
#             existing = FavoriteItem.objects.filter_by_type(model_type=Place,
#                             model_instance=place,
#                             user=request.user)
#             if action == 'addfav':
#                 if len(existing) > 0:
#                     # despite non-action, we count this as a success
#                     return success('item already in favorites')
#                 else:
#                     FavoriteItem.objects.create(user=request.user,
#                                                 content_object=place)
#                     return success('added')
#             elif action == 'removefav':
#                 if len(existing) > 0:
#                     existing.delete()
#                     return success('removed')
#                 else:
#                     # despite non-action, we count this as a success
#                     return success('item not in favorites')
#         else:
#             return failure('invalid action')


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
    try:
        page_num = int(request.GET.get('p', '1'))
    except ValueError:
        page_num = 1

    try:
        page = paginator.page(page_num)
    except (EmptyPage, InvalidPage):
        page = paginator.page(paginator.num_pages)

    items = [PlaceContext(place, user=request.user) for place in page.object_list]

    page_context = PageContext(request, 'places', dict(
        items=items,
        prev_p=page.previous_page_number() if page.has_previous() else None,
        next_p=page.next_page_number() if page.has_next() else None))
    return render_page('places/page_feed.html', page_context)


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
    details = PlaceContext(place, user=request.user)

    # build related feeds viewmodel
    related_feeds = PlaceRelatedFeeds(place, user=request.user)

    # as long as there was no AJAX-requested action, we will return a fully rendered new page
    page_context = PageContext(request, 'places', dict(
                            place_context=details,
                            related_feeds=related_feeds))

    return render_page('places/page_place.html', page_context)


@jsonp_response
def feed_app(request):
    return []


@jsonp_response
def detail_app(request, pid):
    return {}
