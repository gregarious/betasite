from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator, EmptyPage, InvalidPage

# from onlyinpgh.common.utils.jsontools import jsonp_response
from onlyinpgh.common.views import render_page
from onlyinpgh.common.contexts import PageContext

from onlyinpgh.specials.models import Special
from onlyinpgh.specials.contexts import SpecialContext


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
    try:
        page_num = int(request.GET.get('p', '1'))
    except ValueError:
        page_num = 1

    try:
        page = paginator.page(page_num)
    except (EmptyPage, InvalidPage):
        page = paginator.page(paginator.num_pages)

    items = [SpecialContext(special, user=request.user) for special in page.object_list]
    page_context = PageContext(request, 'specials', dict(
        items=items,
        prev_p=page.previous_page_number() if page.has_previous() else None,
        next_p=page.next_page_number() if page.has_next() else None))
    return render_page('specials/page_feed.html', page_context)


def page_details(request, sid):
    '''
    View displays single specials.
    '''
    # build and render special detail viewmodel
    special = get_object_or_404(Special, id=sid)
    details = SpecialContext(special, user=request.user)
    page_context = PageContext(request, 'specials', {'special_context': details})

    return render_page('specials/page_special.html', page_context)


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
