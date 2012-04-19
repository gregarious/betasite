'''Views for AJAX purposes'''
from onlyinpgh.common.utils.jsontools import jsonp_response
from onlyinpgh.places.models import Place
from onlyinpgh.common.core.rendering import render_safe

from django.shortcuts import get_object_or_404, render

from django.http import HttpResponseForbidden

from django.views.decorators.csrf import csrf_protect
from django.template import RequestContext

from onlyinpgh.orgadmin.forms import SimplePlaceForm
from onlyinpgh.common.utils import get_std_thumbnail


### Shotcuts for authentication ###
def authentication_required_403(view_func):
    '''
    If user not authenticated a 403 will be returned.
    '''
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated():
            return view_func(request, *args, **kwargs)
        else:
            return HttpResponseForbidden()
    return wrapper


def _autocomplete_response(request, place_choices, term, limit=4):
    '''
    Return a Python dict with sorted autocomplete responses.
    '''
    match_status = []
    for p in place_choices:
        name = p.name.lower().strip()
        if name and name.startswith(term):
            match_status.append(1)
        elif name and any(word.startswith(term) for word in name.split()):
            match_status.append(2)
        else:
            match_status.append(3)

    results = []
    for _, p in sorted(zip(match_status, place_choices))[:limit]:
        try:
            thumb = get_std_thumbnail(p.image, 'autocomplete') if p.image else None
        except IOError:
            thumb = None
        image_url = thumb.url if thumb else '/static/img/default-place.png'
        results.append({
            'id': p.id,
             'name': p.name,
             'image_url': image_url,
             'address': p.location.address if p.location else '',
             'selected': render_safe('orgadmin/ac_place_selected.html', place=p, context_instance=RequestContext(request))
        })
    return results


@authentication_required_403
@jsonp_response
def place_claim_autocomplete(request):
    '''
    Autocomplete portal that doesn't include the user's owned
    organizations in the return list.
    '''
    term = request.GET.get('term')
    if not term:
        return []

    org = request.session.get('current_org')
    owned_pks = [o.pk for o in org.establishments.all()] if org else []
    places = Place.objects.exclude(pk__in=owned_pks).filter(name__icontains=term)

    return _autocomplete_response(request, places, term, 4)


@authentication_required_403
@jsonp_response
def place_autocomplete(request):
    '''
    Default autocomplete portal.
    '''
    term = request.GET.get('term')
    if not term:
        return []
    places = Place.objects.filter(name__icontains=term)
    return _autocomplete_response(request, places, term, 4)


@authentication_required_403
def place_confirm_div(request):
    '''
    Returns a rendered ac_place_confirm.html template for the place id in
    GET['pid'].
    '''
    pid = request.GET.get('pid', '-1')   # will trigger 404 below
    place = get_object_or_404(Place, id=pid)
    return render(request, 'orgadmin/ac_place_confirm.html', {'place': place})


@authentication_required_403
@csrf_protect
@jsonp_response
def newplace_form_submission(request):
    if request.POST:
        print request.POST
        form = SimplePlaceForm(data=request.POST, prefix='newplace')
        if form.is_valid():
            # if the form didn't give at least a place name or addres, don't save the junk
            if form.cleaned_data['name'] != '' or form.cleaned_data['address'] != '':
                place = form.save(commit=False)
                place.listed = False
                # save manully, including inner model reassign hack
                place.location.save()
                place.location = place.location
                place.save()
                return {
                    'id': place.id,
                    'name': place.name,
                    'address': place.location.address,
                    'selected': render_safe('orgadmin/ac_place_selected.html', place=place, context_instance=RequestContext(request))
                }
    return False
