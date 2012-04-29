from django.shortcuts import get_object_or_404, render_to_response
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from onlyinpgh.common.utils.jsontools import serialize_resources, jsonp_response, sanitize_json
from onlyinpgh.common.views import PageContext

from onlyinpgh.specials.models import Special
from onlyinpgh.specials.viewmodels import SpecialData
from onlyinpgh.specials.resources import SpecialFeedResource

import json


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
    p = request.GET.get('p')
    try:
        page = paginator.page(p)
    except PageNotAnInteger:
        page = paginator.page(1)
    except EmptyPage:
        page = paginator.page(paginator.num_pages)

    specials = page.object_list
    items = [SpecialData(special, user=request.user) for special in specials]
    # need the items in json form for bootstrapping to BB models
    # # temp disabled
    # items_json = serialize_resources(SpecialFeedResource(), items)
    items_json = sanitize_json(json.dumps([item.serialize() for item in items]))

    content = {'items': items,
               'items_json': items_json,
               'prev_p': page.previous_page_number() if page.has_previous() else None,
               'next_p': page.next_page_number() if page.has_next() else None}

    page_context = PageContext(request,
        current_section='specials',
        page_title='Scenable | Oakland Specials',
        content_dict=content)
    return render_to_response('specials/page_feed.html', context_instance=page_context)


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

    return render_to_response('specials/page_special.html', context_instance=page_context)



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
