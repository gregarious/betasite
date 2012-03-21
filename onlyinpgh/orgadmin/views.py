from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.template.loader import render_to_string
from django.template import RequestContext
from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse
from django.forms.util import ErrorList
from django.contrib.auth import login, authenticate, logout
from django.shortcuts import get_object_or_404, redirect

from onlyinpgh.organizations.models import Organization
from onlyinpgh.places.models import Place
from onlyinpgh.events.models import Event
from onlyinpgh.specials.models import Special

from onlyinpgh.orgadmin.forms import OrgSignupForm, OrgLoginForm, \
        SimpleLocationPlaceForm, PlaceClaimForm, SimpleEventForm, \
        SimpleSpecialForm

from onlyinpgh.places.viewmodels import PlaceFeedItem
from onlyinpgh.events.viewmodels import EventFeedItem
from onlyinpgh.specials.viewmodels import SpecialFeedItem

from onlyinpgh.common.core.rendering import render_viewmodels_as_ul


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
            print 'all good!'
            return view_func(request, *args, **kwargs)
        else:
            print 'you shall not pass!'
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
        form = OrgSignupForm(request.POST)
        # test if the browser supports cookies
        if request.session.test_cookie_worked():
            request.session.delete_test_cookie()
        else:
            errors = form._errors.setdefault("__all__", ErrorList())
            errors.append(u"Your browser must support cookies to use this site.")

        if form.is_valid():
            form.save()     # saves new user

        # authenticate new user, create  and log in
        user = authenticate(username=form.username, password=form.password1)
        login(request, user)

        # create new organization for user to administer
        org = Organization.objects.create(name=form.orgname)
        org.administrators.add(user)

        request.session['current_org'] = org

        # redirect to home page
        redirect_to = reverse('orgadmin-home')
        return HttpResponseRedirect(redirect_to)
    else:
        form = OrgSignupForm()

    request.session.set_test_cookie()
    context = RequestContext(request)
    content = render_to_string('orgadmin/signup_form.html',
        {'form': form}, context_instance=context)

    return response_admin_page(content, context)


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
        form = OrgLoginForm()

    request.session.set_test_cookie()
    context = RequestContext(request)
    content = render_to_string('orgadmin/login_form.html',
        {'form': form}, context_instance=context)

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
            return redirect('orgadmin.views.page_list_places')
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
        form = SimpleLocationPlaceForm(data=request.POST,
            instance=instance)
        if form.is_valid():
            place = form.save()

            # if a new place, it won't be a part of the current org's
            # list of establishments. add it now.
            if place not in org.establishments.all():
                org.establishments.add(place)

            return redirect('orgadmin.views.page_list_places')
    else:
        form = SimpleLocationPlaceForm(instance=instance)

    context = RequestContext(request, {'current_org': org})
    content = render_to_string('orgadmin/place_setup_wizard.html', {'form': form},
        context_instance=context)
    return response_admin_page(content, context)


@authentication_required
def page_edit_place(request, id):
    org = request.session.get('current_org')
    instance = get_object_or_404(Place, id=id)
    if not org or not org_owns(org, instance):
        return HttpResponseForbidden()

    if request.POST:
        form = SimpleLocationPlaceForm(data=request.POST, instance=instance)
        if form.is_valid():
            form.save()
            return redirect('orgadmin.views.page_list_places')
    else:
        form = SimpleLocationPlaceForm(instance=instance)

    context = RequestContext(request, {'current_org': org})
    content = render_to_string('orgadmin/place_edit_form.html', {'form': form}, context_instance=context)
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

    if request.POST:
        form = SimpleEventForm(organization=org, data=request.POST, instance=instance)
        if form.is_valid():
            form.save()
            return redirect('orgadmin.views.page_list_events')
    else:
        form = SimpleEventForm(organization=org, instance=instance)

    context = RequestContext(request, {'current_org': org})
    content = render_to_string('orgadmin/event_edit_form.html', {'form': form},
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
            return redirect('orgadmin.views.page_list_specials')
    else:
        form = SimpleSpecialForm(organization=org, instance=instance)

    context = RequestContext(request, {'current_org': org})
    content = render_to_string('orgadmin/special_edit_form.html', {'form': form},
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
