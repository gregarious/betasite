from django.shortcuts import get_object_or_404, render_to_response
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from onlyinpgh.common.utils.jsontools import serialize_resources, jsonp_response
from onlyinpgh.common.views import PageContext

from onlyinpgh.specials.models import Special
from onlyinpgh.specials.viewmodels import SpecialData
from onlyinpgh.specials.resources import SpecialFeedResource


def page_feed(request):
    '''
    View function that handles a page load request for a feed of place
    items.

    Renders page.html with main_content set to the rendered HTML of
    a feed.
    '''
    # get a list of rendered items
    all_specials = Special.objects.all()
    paginator = Paginator(all_specials, 10)
    page = request.GET.get('p')
    try:
        specials = paginator.page(page)
    except PageNotAnInteger:
        specials = paginator.page(1)
    except EmptyPage:
        specials = paginator.page(paginator.num_pages)

    items = [SpecialData(special, user=request.user) for special in specials]
    # need the items in json form for bootstrapping to BB models
    items_json = serialize_resources(SpecialFeedResource(), specials, request=request)

    content = {'items': items,
               'items_json': items_json,
               'prev_p': page.previous_page_number() if page.has_previous() else None,
               'next_p': page.next_page_number() if page.has_next() else None}

    page_context = PageContext(request,
        current_section='specials',
        page_title='Scenable | Oakland Specials',
        content_dict=content)
    return render_to_response('specials/page_feed.html', page_context)


def page_details(request, sid):
    '''
    View displays single specials.
    '''
    # build and render special detail viewmodel
    special = get_object_or_404(Special, id=sid)
    details = SpecialData(special, user=request.user)
    content = {'special': details}
    page_context = PageContext(request,
        current_section='specials',
        page_title='Scenable | %s' % special.title,
        content_dict=content)

    return render_to_response('specials/page_event.html', page_context)



# @jsonp_response
# def feed_app(request):
#     offers = []
#     for s in Offer.objects.all()[:10]:
#         special = {
#             'id':   s.id,
#             'description': s.description,
#             'points': s.point_value,
#             'sponsor': s.sponsor.name if s.sponsor else None,
#             'tags': [{'name':item.tag.name} for item in p.tags.all() if item.tag.name != 'establishment']
#         }
#         offers.append(special)

#     return {'offers': offers}    # decorator will handle JSONP details


# @jsonp_response
# def detail_app(request, oid):
#     o = Offer.objects.get(id=oid)
#     special = {
#         'id':   o.id,
#         'description': o.description,
#         'points': o.point_value,
#         'sponsor': o.sponsor.name if o.sponsor else None,
#         'tags': [{'name':item.tag.name} for item in o.tags.all() if item.tag.name != 'establishment']
#     }

#     return {'special':special}
