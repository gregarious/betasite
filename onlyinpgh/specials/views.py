from django.shortcuts import get_object_or_404

from onlyinpgh.common.utils.jsontools import jsonp_response, package_json_response
from onlyinpgh.common.core.rendering import render_viewmodel, render_safe
from onlyinpgh.common.views import page_response, render_main

from onlyinpgh.specials.models import Special
from onlyinpgh.specials.viewmodels import SpecialFeedItem, SpecialDetail


def render_feed(specials, feed_template, user=None, item_template='specials/feed_item.html'):
    '''
    Returns a rendered specials feed.
    '''
    items = [SpecialFeedItem(special, user=user) for special in specials]
    rendered_items = [render_viewmodel(item, item_template) for item in items]
    return render_safe(feed_template, items=rendered_items)


def page_feed(request):
    '''
    View function that handles a page load request for a feed of place
    items.

    Renders page.html with main_content set to the rendered HTML of
    a feed.
    '''
    # get a list of rendered items
    feed = render_feed(Special.objects.all()[:10],
        feed_template='specials/main_feed.html', user=request.user)
    main = render_main(feed)
    return page_response(main, request)


def page_details(request, sid):
    '''
    View displays single specials.
    '''
    # build and render special detail viewmodel
    special = get_object_or_404(Special, id=sid)
    details = SpecialDetail(special, user=request.user)
    content = render_viewmodel(details,
                template='specials/single.html',
                class_label='special-single')
    main = render_main(content)
    return page_response(main, request)


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
