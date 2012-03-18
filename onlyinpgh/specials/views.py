from django.shortcuts import render
from django.utils.safestring import mark_safe
from django.template import RequestContext
from django.template.loader import render_to_string

from onlyinpgh.specials.models import Special


def biz_edit_special(request, sid):
    form = None
    form_html = mark_safe(render_to_string(
        'specials/manage/edit_special.html', {'form': form, 'mode': 'edit'},
        context_instance=RequestContext(request)))
    return render(request, 'manage_base.html', {'content': form_html})


def biz_add_special(request):
    form = None
    form_html = mark_safe(render_to_string(
        'specials/manage/edit_special.html', {'form': form, 'mode': 'add'},
        context_instance=RequestContext(request)))
    return render(request, 'manage_base.html', {'content': form_html})


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
