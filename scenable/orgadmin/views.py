from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, logout
from django.shortcuts import get_object_or_404, redirect, render, render_to_response
from django.template import RequestContext
from scenable.common.core.rendering import render_safe

from scenable.organizations.models import Organization

from scenable.places.models import Place
from scenable.places.viewmodels import PlaceData
from scenable.events.models import Event, Role
from scenable.events.viewmodels import EventData
from scenable.specials.models import Special
from scenable.specials.viewmodels import SpecialData

from scenable.tags.models import Tag

from scenable.accounts.forms import RegistrationForm, RememberMeForm
from scenable.orgadmin.forms import SimpleOrgForm, OrgLoginForm, OrgAdminPlaceForm, SimplePlaceForm,\
                                     PlaceClaimForm, SimpleEventForm, SimpleSpecialForm
from scenable.accounts.views import login

import re


class ManagePageContext(RequestContext):
    '''
    Used for main context variable for every main site page.
    '''
    def __init__(self, request, current_org=None, page_title=None, content_dict={}, **kwargs):
        '''
        content_dict: context variables for main_context
        '''
        if page_title is None:
            page_title = "Scenable Business Account"
            if current_org:
                page_title += " | %s" % current_org.name

        variables = dict(
            page_title=page_title,
            current_org=current_org,
        )
        if not current_org and request.user.is_authenticated():
            current_org = _get_current_org(request.user)
        variables['current_org'] = current_org
        variables.update(content_dict)
        super(ManagePageContext, self).__init__(request, variables, **kwargs)


def _redirect_home(request, notification_type=None):
    if notification_type is not None:
        request.session['home-notification'] = notification_type
    return redirect('orgadmin-home')


def _get_current_org(user):
    # just default to first org in the list for now
    owned_orgs = Organization.objects.filter(administrators=user)
    if len(owned_orgs) > 0:
        return owned_orgs[0]
    else:
        return None


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

    # short circuit for event instances: also allow Role ownership over the event
    if isinstance(instance, Event):
        if Role.objects.filter(event=instance, organization=org, role_type='owner').count() > 0:
            return True
    try:
        return instance.place in establishments
    except AttributeError:
        return instance in establishments


### URL-linked page views ###
def page_index(request):
    if request.user.is_authenticated():
        return redirect('orgadmin-home')
    else:
        return render(request, 'orgadmin/splash.html')


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

                # redirect to home page
                return _redirect_home(request, notification_type=1)
            else:   # if cookies aren't enabled, go to login page
                return redirect('orgadmin-login')
    else:
        reg_form = RegistrationForm(prefix='reg')
        org_form = SimpleOrgForm(prefix='org')

    request.session.set_test_cookie()

    context = ManagePageContext(request, content_dict=dict(
        registration_form=reg_form,
        org_form=org_form,
        remember_me=RememberMeForm(),
    ))
    return render_to_response('orgadmin/page_signup.html', context_instance=context)


def page_login(request):
    if request.user.is_authenticated():
        logout(request)

    if request.POST:
        # passing in request checks for cookies
        form = OrgLoginForm(request, data=request.POST)
        if form.is_valid():
            if request.session.test_cookie_worked():
                request.session.delete_test_cookie()

            user = form.get_user()
            login(request, user)

            # redirect to homepage
            redirect_to = reverse('orgadmin-home')
            return HttpResponseRedirect(redirect_to)
    else:
        form = OrgLoginForm()

    request.session.set_test_cookie()

    context = ManagePageContext(request, content_dict=dict(
        form=form,
        form_action=reverse('orgadmin-login'),
        remember_me=RememberMeForm(),
    ))
    return render_to_response('orgadmin/page_login.html', context_instance=context)


def page_logout(request):
    logout(request)
    # redirect to homepage
    return HttpResponseRedirect(
        reverse('orgadmin-login'))


@authentication_required
def page_home(request):
    '''
    notification types:
    1: Welcome message
    2: No org warning
    3: No place message for special adding
    '''
    try:
        notification_type = str(request.session.pop('home-notification'))
    except KeyError:
        notification_type = None
    content = {'notification_type': notification_type}
    context = ManagePageContext(request, content_dict=content)
    return render_to_response('orgadmin/page_home.html', context_instance=context)


@authentication_required
def page_link_org(request):
    context = ManagePageContext(request)

    if request.POST:
        form = SimpleOrgForm(request.POST)
        if form.is_valid():
            org = form.save()   # saves new org
            org.administrators.add(request.user)
            return redirect('orgadmin-home')
    else:
        form = SimpleOrgForm()

    context = ManagePageContext(request, content_dict=dict(
        form=form
    ))

    return render_to_response('orgadmin/page_link_org.html', context_instance=context)


@authentication_required
def page_claim_place(request):
    '''
    View displays place claim page to an authorized user with an organization.

    Page includes a form for claiming a Place not already owned, or a link
    to create a new place. The resulting action for either choice is to bring
    up the place setup wizard.
    '''
    org = _get_current_org(request.user)
    if not org:
        return _redirect_home(request, notification_type=2)

    all_places = Place.objects.all()
    owned_places = org.establishments.all()
    unowned_places = [p for p in all_places if p not in owned_places]

    if request.POST:
        form = PlaceClaimForm(place_choices=unowned_places, data=request.POST)
        if form.is_valid():
            id_str = form.cleaned_data['place']
            org.establishments.add(Place.objects.get(id=int(id_str)))
            return redirect('orgadmin-editplace', id_str)
    else:
        form = PlaceClaimForm(place_choices=unowned_places)

    context = ManagePageContext(request, content_dict={'form': form})
    return render_to_response('orgadmin/page_place_claim.html', context_instance=context)


@authentication_required
def page_edit_place(request, id=None):
    org = _get_current_org(request.user)
    if id is not None:
        instance = get_object_or_404(Place, id=id)
        if not org or not org_owns(org, instance):
            return HttpResponseForbidden()
    else:
        instance = None
        if not org:
            return _redirect_home(request, notification_type=2)

    if request.POST:
        # clean up possible artifacts in fb/twitter fields (full urls, @ symbols)
        fb_id = request.POST.get('fb_id', '')
        if 'facebook.com' in fb_id:
            request.POST.update({'fb_id': fb_id.strip().strip('/').split('/')[-1]})
        twitter = request.POST.get('twitter_username', '').strip()
        if twitter.startswith('@'):
            request.POST.update({'twitter_username': twitter.strip().lstrip('@')})

        form = OrgAdminPlaceForm(data=request.POST, files=request.FILES,
            instance=instance)
        if form.is_valid():
            place = form.save()

            # if a new place, it won't be a part of the current org's
            # list of establishments. add it now.
            if not instance and place not in org.establishments.all():
                org.establishments.add(place)

            return redirect('orgadmin-listplaces')
    else:
        form = OrgAdminPlaceForm(instance=instance)

    context = ManagePageContext(request, content_dict=dict(
        form=form,
        tag_names=[t.name for t in Tag.objects.all()]
    ))
    return render_to_response('orgadmin/page_place_edit.html', context_instance=context)


@authentication_required
def page_remove_place(request, id):
    org = _get_current_org(request.user)
    instance = get_object_or_404(Place, id=id)
    if not org or not org_owns(org, instance):
        return HttpResponseForbidden()
    org.establishments.remove(instance)
    return redirect('orgadmin-listplaces')


@authentication_required
def page_list_places(request):
    org = _get_current_org(request.user)
    places = org.establishments.all() if org else []
    items = [PlaceData(place) for place in places]

    context = ManagePageContext(request, content_dict={'items': items})
    return render_to_response('orgadmin/page_place_list.html', context_instance=context)


@authentication_required
def page_delete_event(request, id):
    org = _get_current_org(request.user)
    instance = get_object_or_404(Event, id=id)
    if not org or not org_owns(org, instance):
        return HttpResponseForbidden()
    instance.delete()
    return redirect('orgadmin-listevents')


@authentication_required
def page_edit_event(request, id=None):
    '''
    Edit an Event. If id is None, the form is for a new Event entry.
    '''
    org = _get_current_org(request.user)
    initial = {}
    if id is not None:
        instance = get_object_or_404(Event, id=id)
        if not org or not org_owns(org, instance):
            return HttpResponseForbidden()
    else:
        instance = None
        if not org:
            return _redirect_home(request, notification_type=2)
        if org and org.establishments.count() == 1:
            initial['place'] = org.establishments.all()[0].id

    if request.POST or request.FILES:
        form = SimpleEventForm(data=request.POST, files=request.FILES, instance=instance, initial=initial)
        if form.is_valid():
            event = form.save()
            Role.objects.get_or_create(role_type='owner', organization=org, event=event)
            return redirect('orgadmin-listevents')
    else:
        form = SimpleEventForm(instance=instance, initial=initial)

    # TODO: awesome "initial_selected" hack for autocomplete display!!!!
    match = re.search('name="place" value="(\d+)"', form.as_ul())
    if match:
        try:
            initial_place = Place.objects.get(id=match.group(1))
            initial_selected = render_safe('orgadmin/ac_place_selected.html', context_instance=RequestContext(request), place=initial_place)
        except Place.DoesNotExist:
            initial_selected = None
    else:
        initial_selected = None

    context = ManagePageContext(request, content_dict=dict(
        form=form,
        tag_names=[t.name for t in Tag.objects.all()],
        newplace_form=SimplePlaceForm(prefix='newplace', initial={'state': 'PA', 'postcode': '15213', 'town': 'Pittsburgh'}),
        initial_selected=initial_selected
    ))
    return render_to_response('orgadmin/page_event_edit.html', context_instance=context)


@authentication_required
def page_list_events(request):
    org = _get_current_org(request.user)
    establishments = org.establishments.all() if org else []

    events = [role.event for role in Role.objects.filter(role_type='owner', organization=org)] if org else []
    events = set(events).union(Event.objects.filter(place__in=establishments))
    items = [EventData(event) for event in events]

    context = ManagePageContext(request, content_dict={'items': items})
    return render_to_response('orgadmin/page_event_list.html', context_instance=context)


@authentication_required
def page_delete_special(request, id):
    org = _get_current_org(request.user)
    instance = get_object_or_404(Special, id=id)
    if not org or not org_owns(org, instance):
        return HttpResponseForbidden()
    instance.delete()
    return redirect('orgadmin-listspecials')


@authentication_required
def page_edit_special(request, id=None):
    '''
    Edit a Special. If id is None, the form is for a new Special entry.
    '''
    org = _get_current_org(request.user)
    if id is not None:
        instance = get_object_or_404(Special, id=id)
        if not org or not org_owns(org, instance):
            return HttpResponseForbidden()
    else:
        instance = None
        if not org:
            return _redirect_home(request, notification_type=2)
        if org.establishments.count() == 0:
            return _redirect_home(request, notification_type=3)

    if request.POST:
        form = SimpleSpecialForm(organization=org, data=request.POST, instance=instance)
        if form.is_valid():
            form.save()
            return redirect('orgadmin-listspecials')
    else:
        form = SimpleSpecialForm(organization=org, instance=instance)

    context = ManagePageContext(request, content_dict=dict(
        form=form,
        tag_names=[t.name for t in Tag.objects.all()]
    ))
    return render_to_response('orgadmin/page_special_edit.html', context_instance=context)


@authentication_required
def page_list_specials(request):
    org = _get_current_org(request.user)
    establishments = org.establishments.all() if org else []
    specials = Special.objects.filter(place__in=establishments)
    items = [SpecialData(special) for special in specials]

    context = ManagePageContext(request, content_dict={'items': items})
    return render_to_response('orgadmin/page_special_list.html', context_instance=context)
