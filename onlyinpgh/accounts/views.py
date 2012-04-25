from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse

from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required

from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect

from onlyinpgh.accounts.forms import RegistrationForm, UserProfileForm, ActivityPreferencesForm, CredentialsForm
from onlyinpgh.common.views import PageContext

import urlparse

from onlyinpgh.places.models import Favorite
from onlyinpgh.places.viewmodels import PlaceData

from onlyinpgh.events.models import Attendee
from onlyinpgh.events.viewmodels import EventData

from onlyinpgh.specials.models import Coupon
from onlyinpgh.specials.viewmodels import SpecialData


@csrf_protect
@never_cache
def page_login(request, redirect_field_name='next'):
    '''
    Renders login page.
    '''
    redirect_to = request.REQUEST.get(redirect_field_name, '')
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            netloc = urlparse.urlparse(redirect_to)[1]

            # Use default setting if redirect_to is empty
            if not redirect_to:
                redirect_to = reverse('home')

            # Security check -- don't allow redirection to a different
            # host.
            elif netloc and netloc != request.get_host():
                redirect_to = reverse('home')

            # Okay, security checks complete. Log the user in.
            login(request, form.get_user())

            if request.session.test_cookie_worked():
                request.session.delete_test_cookie()

            return HttpResponseRedirect(redirect_to)
    else:
        form = AuthenticationForm(request)
    request.session.set_test_cookie()

    content = dict(
        form=form,
        form_action=reverse('login'),
        next=redirect_to
    )
    context = PageContext(request,
        page_title='Scenable | Login',
        content_dict=content)
    return render_to_response('registration/page_login.html', context)


def page_signup(request):
    # if POST request, handle the form submission
    if request.POST:
        reg_form = RegistrationForm(request.POST, prefix='reg')
        profile_form = UserProfileForm(request.POST, prefix='prof')

        if reg_form.is_valid() and profile_form.is_valid():
            user = reg_form.save()     # saves new user

            # reinitialize the form linked to the new user profile
            profile_form = UserProfileForm(data=request.POST,
                instance=user.get_profile(), prefix='prof')
            profile_form.save()

            # test if the browser supports cookies
            if request.session.test_cookie_worked():
                request.session.delete_test_cookie()

                # authenticate new user and log in
                user = authenticate(username=reg_form.cleaned_data['username'],
                    password=reg_form.cleaned_data['password1'])
                login(request, user)

                # redirect to home page
                redirect_to = reverse('home')
            else:   # if cookies aren't enabled, go to login page
                redirect_to = reverse('login')

            return HttpResponseRedirect(redirect_to)
    else:
        reg_form = RegistrationForm(prefix='reg')
        profile_form = UserProfileForm(prefix='prof')

    request.session.set_test_cookie()

    content = dict(
        registration_form=reg_form,
        profile_form=profile_form,
        form_action=reverse('signup')
    )
    context = PageContext(request,
        page_title='Scenable | Sign Up',
        content_dict=content)
    return render_to_response('registration/page_signup.html', context)


def _render_profile_page(request, user, current_panel, variables):
    variables['profile'] = user.get_profile()
    variables['current_panel'] = current_panel
    context = PageContext(request,
        current_section='accounts',
        page_title='Scenable | %s\'s Profile' % user.username,
        content_dict=variables)
    print context
    return render_to_response('accounts/page_profile.html', context)


@login_required
def page_manage_account(request):
    '''
    Main profile page view function, all panels are generated through here.
    - user is the User whose profile is being generated
    - current_panel is an enum string with on of the following values:
        account, places, events, specials.
    '''
    # get user to manage, ensure logged in user has permissions
    # create/process the 3 forms
    user = request.user
    forms = dict(
        profile_form=UserProfileForm(),
        credentials_form=CredentialsForm(),
        preferences_form=ActivityPreferencesForm())
    return _render_profile_page(request, user, 'account', {'account_forms': forms})


@login_required
def page_user_favorites(request):
    # TODO: allow non-self user queries
    user = request.user
    places = [fav.place for fav in Favorite.objects.filter(user=user, is_favorite=True)]
    items = [PlaceData(place, user=request.user) for place in places]
    return _render_profile_page(request, user, 'places', {'feed_items': items})


@login_required
def page_user_attendance(request):
    # TODO: allow non-self user queries
    user = request.user
    events = [att.event for att in Attendee.objects.filter(user=user, is_attending=True)]
    items = [EventData(event, user=request.user) for event in events]
    return _render_profile_page(request, user, 'events', {'feed_items': items})


@login_required
def page_user_coupons(request):
    # TODO: allow non-self user queries
    user = request.user
    specials = [coupon.special for coupon in Coupon.objects.filter(user=user, was_used=False)]
    items = [SpecialData(special, user=request.user) for special in specials]
    return _render_profile_page(request, user, 'specials', {'feed_items': items})
