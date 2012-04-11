from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.template.loader import render_to_string
from django.template import RequestContext
from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse
from django.contrib.auth import login, authenticate, logout
from django.shortcuts import get_object_or_404, redirect

from onlyinpgh.organizations.models import Organization
from onlyinpgh.places.models import Place
from onlyinpgh.events.models import Event
from onlyinpgh.specials.models import Special
from onlyinpgh.tags.models import Tag

from django.contrib.auth.forms import AuthenticationForm
from onlyinpgh.accounts.forms import RegistrationForm
from onlyinpgh.orgadmin.forms import SimpleOrgForm, OrgAdminPlaceForm, SimplePlaceForm,\
                                     PlaceClaimForm, SimpleEventForm, SimpleSpecialForm

from onlyinpgh.places.viewmodels import PlaceFeedItem
from onlyinpgh.events.viewmodels import EventFeedItem
from onlyinpgh.specials.viewmodels import SpecialFeedItem

from onlyinpgh.common.core.rendering import render_viewmodels_as_ul, render_safe


def render_admin_page(safe_content, context_instance=None):
    '''
    Renders a page in the admin interface.
    '''
    content = {
        'content': mark_safe(safe_content)
    }
    return render_to_string('orgadmin/base.html',
        content, context_instance=context_instance)


def response_admin_page(safe_content, context_instance=None):
    return HttpResponse(render_admin_page(safe_content, context_instance))


### Shotcuts for authentication ###
def authentication_required(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated():
            return view_func(request, *args, **kwargs)
        else:
            return HttpResponseRedirect(reverse('orgadmin-login'))
    return wrapper


def org_owns(org, instance):
    '''
    Ensures the given organization has access to edit instance.

    If instance is a Place, will check org.establishments directly. If
    instance is not a Place, it must have a place property, which will
    be checked instead.
    '''
    establishments = org.establishments.all()

    try:
        return instance.place in establishments
    except AttributeError:
        return instance in establishments


### URL-linked page views ###
def page_signup(request):
    if request.user.is_authenticated():
        logout(request)

    if request.POST:
        reg_form = RegistrationForm(request.POST, prefix='reg')
        org_form = SimpleOrgForm(request.POST, prefix='org')

        if reg_form.is_valid() and org_form.is_valid():
            reg_form.save()     # saves new user
            org = org_form.save()   # saves new org

            # test if the browser supports cookies
            if request.session.test_cookie_worked():
                request.session.delete_test_cookie()

                # authenticate new user and log in
                user = authenticate(username=reg_form.cleaned_data['username'],
                    password=reg_form.cleaned_data['password1'])
                login(request, user)

                # set user as administrator to given org
                org.administrators.add(user)

                request.session['current_org'] = org

                # redirect to home page
                redirect_to = reverse('orgadmin-home')
            else:   # if cookies aren't enabled, go to login page
                redirect_to = reverse('orgadmin-login')

            return HttpResponseRedirect(redirect_to)
    else:
        reg_form = RegistrationForm(prefix='reg')
        org_form = SimpleOrgForm(prefix='org')

    request.session.set_test_cookie()
    context = RequestContext(request)
    content = render_to_string('orgadmin/signup_form.html',
        {'registration_form': reg_form, 'org_form': org_form},
        context_instance=context)

    return response_admin_page(content, context)


def page_login(request):
    if request.user.is_authenticated():
        logout(request)

    if request.POST:
        # passing in request checks for cookies
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            if request.session.test_cookie_worked():
                request.session.delete_test_cookie()

            user = form.get_user()
            login(request, user)

            # just default to first org in the list for now
            owned_orgs = Organization.objects.filter(administrators=user)
            if len(owned_orgs) > 0:
                request.session['current_org'] = owned_orgs[0]
            else:
                request.session['current_org'] = None

            # redirect to homepage
            redirect_to = reverse('orgadmin-home')
            return HttpResponseRedirect(redirect_to)
    else:
        form = AuthenticationForm()

    request.session.set_test_cookie()
    context = RequestContext(request)
    content = render_to_string('registration/login_form.html',
        {'form': form, 'form_action': reverse('orgadmin-login')},
        context_instance=context)

    return response_admin_page(content, context)


def page_logout(request):
    logout(request)
    # redirect to homepage
    return HttpResponseRedirect(
        reverse('orgadmin-login'))


@authentication_required
def page_home(request):
    context = RequestContext(request,
        {'current_org': request.session.get('current_org')})
    content = render_to_string('orgadmin/home.html', context_instance=context)
    return response_admin_page(content, context)


@authentication_required
def page_claim_place(request):
    '''
    View displays place claim page to an authorized user with an organization.

    Page includes a form for claiming a Place not already owned, or a link
    to create a new place. The resulting action for either choice is to bring
    up the place setup wizard.
    '''
    org = request.session.get('current_org')
    if not org:
        return redirect('orgadmin-home')

    all_places = Place.objects.all()
    owned_places = org.establishments.all()
    unowned_places = [p for p in all_places if p not in owned_places]

    if request.POST:
        form = PlaceClaimForm(place_choices=unowned_places, data=request.POST)
        if form.is_valid():
            id_str = form.cleaned_data['place']
            org.establishments.add(Place.objects.get(id=int(id_str)))
            return redirect('onlyinpgh.orgadmin.views.page_edit_place', id_str)
    else:
        form = PlaceClaimForm(place_choices=unowned_places)

    context = RequestContext(request,
        {'current_org': org})
    content = render_to_string('orgadmin/place_claim.html', {'form': form},
                context_instance=context)
    return response_admin_page(content, context)


@authentication_required
def page_setup_place_wizard(request, id=None):
    org = request.session.get('current_org')
    if id is not None:
        instance = get_object_or_404(Place, id=id)
        if not org or not org_owns(org, instance):
            return HttpResponseForbidden()
    else:
        instance = None
        # TODO: home page needs some kind of message if user has no org
        if not org:
            return redirect('orgadmin-home')

    if request.POST:
        form = OrgAdminPlaceForm(data=request.POST,
            instance=instance)
        if form.is_valid():
            place = form.save()

            # if a new place, it won't be a part of the current org's
            # list of establishments. add it now.
            if place not in org.establishments.all():
                org.establishments.add(place)

            return redirect('onlyinpgh.orgadmin.views.page_list_places')
    else:
        form = OrgAdminPlaceForm(instance=instance)

    context = RequestContext(request, {'current_org': org})
    content = render_to_string('orgadmin/place_edit_form.html',
        {'form': form, 'tag_names': [t.name for t in Tag.objects.all()]},
        context_instance=context)
    return response_admin_page(content, context)


@authentication_required
def page_remove_place(request, id):
    org = request.session.get('current_org')
    instance = get_object_or_404(Place, id=id)
    if not org or not org_owns(org, instance):
        return HttpResponseForbidden()
    org.establishments.remove(instance)
    return redirect('onlyinpgh.orgadmin.views.page_list_places')


@authentication_required
def page_edit_place(request, id):
    org = request.session.get('current_org')
    instance = get_object_or_404(Place, id=id)
    if not org or not org_owns(org, instance):
        return HttpResponseForbidden()

    if request.POST:
        form = OrgAdminPlaceForm(data=request.POST, instance=instance)
        if form.is_valid():
            form.save()
            return redirect('onlyinpgh.orgadmin.views.page_list_places')
    else:
        form = OrgAdminPlaceForm(instance=instance)

    context = RequestContext(request, {'current_org': org})
    content = render_to_string('orgadmin/place_edit_form.html',
        {'form': form, 'tag_names': [t.name for t in Tag.objects.all()]},
        context_instance=context)
    return response_admin_page(content, context)


@authentication_required
def page_list_places(request):
    org = request.session.get('current_org')
    places = org.establishments.all() if org else []

    items = [PlaceFeedItem(place) for place in places]
    list_content = render_viewmodels_as_ul(items, 'orgadmin/place_item.html')

    context = RequestContext(request, {'current_org': org})
    content = render_to_string('orgadmin/place_list.html', {'list_content': list_content}, context_instance=context)
    return response_admin_page(content, context)


@authentication_required
def page_delete_event(request, id):
    org = request.session.get('current_org')
    instance = get_object_or_404(Event, id=id)
    if not org or not org_owns(org, instance):
        return HttpResponseForbidden()
    instance.delete()
    return redirect('onlyinpgh.orgadmin.views.page_list_events')


@authentication_required
def page_edit_event(request, id=None):
    '''
    Edit an Event. If id is None, the form is for a new Event entry.
    '''
    org = request.session.get('current_org')
    if id is not None:
        instance = get_object_or_404(Event, id=id)
        if not org or not org_owns(org, instance):
            return HttpResponseForbidden()
    else:
        instance = None
        if not org:
            return redirect('orgadmin-home')

    initial_place = None
    if request.POST:
        form = SimpleEventForm(data=request.POST, instance=instance)
        if form.is_valid():
            form.save()
            return redirect('onlyinpgh.orgadmin.views.page_list_events')

        # TODO: fix this "initial_selected" hack for autocomplete display
        initial_place_id = request.POST.get('place')
        if initial_place_id is not None:
            try:
                initial_place = Place.objects.get(id=initial_place_id)
            except Place.DoesNotExist:
                pass
        elif instance and instance.place:
            initial_place = instance.place
    else:
        form = SimpleEventForm(instance=instance)
        if instance and instance.place:
            initial_place = instance.place

    if initial_place is not None:
        initial_selected = render_safe('orgadmin/ac_place_selected.html', place=initial_place)
    else:
        initial_selected = None

    context = RequestContext(request, {'current_org': org})
    content = render_to_string('orgadmin/event_edit_form.html', {
            'form': form,
            'newplace_form': SimplePlaceForm(prefix='newplace', initial={'state': 'PA', 'postcode': '15213', 'town': 'Pittsburgh'}),
            'initial_selected': initial_selected,
            'tag_names': [t.name for t in Tag.objects.all()],
        },
        context_instance=context)
    return response_admin_page(content, context)


@authentication_required
def page_list_events(request):
    org = request.session.get('current_org')
    establishments = org.establishments.all() if org else []
    events = Event.objects.filter(place__in=establishments)
    items = [EventFeedItem(event) for event in events]
    list_content = render_viewmodels_as_ul(items, 'orgadmin/event_item.html')

    context = RequestContext(request, {'current_org': org})
    content = render_to_string('orgadmin/event_list.html', {'list_content': list_content},
                                    context_instance=context)
    return response_admin_page(content, context)


@authentication_required
def page_delete_special(request, id):
    org = request.session.get('current_org')
    instance = get_object_or_404(Special, id=id)
    if not org or not org_owns(org, instance):
        return HttpResponseForbidden()
    instance.delete()
    return redirect('onlyinpgh.orgadmin.views.page_list_specials')


@authentication_required
def page_edit_special(request, id=None):
    '''
    Edit a Special. If id is None, the form is for a new Special entry.
    '''
    org = request.session.get('current_org')
    if id is not None:
        instance = get_object_or_404(Special, id=id)
        if not org or not org_owns(org, instance):
            return HttpResponseForbidden()
    else:
        instance = None
        if not org:
            return redirect('orgadmin-home')

    if request.POST:
        form = SimpleSpecialForm(organization=org, data=request.POST, instance=instance)
        if form.is_valid():
            form.save()
            return redirect('onlyinpgh.orgadmin.views.page_list_specials')
    else:
        form = SimpleSpecialForm(organization=org, instance=instance)

    context = RequestContext(request, {'current_org': org})
    content = render_to_string('orgadmin/special_edit_form.html',
        {'form': form, 'tag_names': [t.name for t in Tag.objects.all()]},
        context_instance=context)
    return response_admin_page(content, context)


@authentication_required
def page_list_specials(request):
    org = request.session.get('current_org')
    establishments = org.establishments.all() if org else []
    specials = Special.objects.filter(place__in=establishments)
    items = [SpecialFeedItem(special) for special in specials]
    list_content = render_viewmodels_as_ul(items, 'orgadmin/special_item.html')

    context = RequestContext(request, {'current_org': org})
    content = render_to_string('orgadmin/special_list.html', {'list_content': list_content},
                                context_instance=context)
    return response_admin_page(content, context)
