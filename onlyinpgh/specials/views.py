from django.shortcuts import render_to_response
from onlyinpgh.offers.models import Offer

from onlyinpgh.common.utils.jsontools import jsonp_response

# def feed_page(request):
#     variables = {'offers': Offer.objects.all()}
#     return render_to_response('offers/offers_page.html', variables)


# def detail_page(request, id):
#     variables = {'o': Offer.objects.get(id=id)}
#     return render_to_response('offers/offers_single.html', variables)


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
