from django.http import HttpResponseRedirect

from django.core.urlresolvers import reverse

from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required

from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect

from onlyinpgh.accounts.forms import RegistrationForm, UserProfileForm, ActivityPreferencesForm, CredentialsForm
from onlyinpgh.common.views import render_page
from onlyinpgh.common.contexts import PageContext

import urlparse

from onlyinpgh.accounts.contexts import PublicProfile

from onlyinpgh.places.models import Favorite
from onlyinpgh.places.contexts import PlaceContext

from onlyinpgh.events.models import Attendee
from onlyinpgh.events.contexts import EventContext

from onlyinpgh.specials.models import Coupon
from onlyinpgh.specials.contexts import SpecialContext


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

    context = PageContext(request, 'accounts', dict(
            form=form,
            form_action=reverse('login'),
            next=redirect_to)
        )
    return render_page('registration/page_login.html', context)


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

    context = PageContext(request, 'accounts', dict(
            registration_form=reg_form,
            profile_form=profile_form,
            form_action=reverse('signup')),
        )
    return render_page('registration/page_signup.html', context)


def _render_profile_page(request, user, current_panel, variables):
    variables.update({
        'profile': user.get_profile(),
        'current_panel': current_panel})
    context = PageContext(request, 'accounts', variables)
    return render_page('accounts/page_profile.html', context)


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
    return _render_profile_page(request, user, 'account',
        {'account_forms': forms})


@login_required
def page_user_favorites(request):
    # TODO: allow non-self user queries
    user = request.user
    places = [fav.place for fav in Favorite.objects.filter(user=user, is_favorite=True)]
    items = [PlaceContext(place, user=request.user) for place in places]
    return _render_profile_page(request, user, 'places', {'items': items})


@login_required
def page_user_attendance(request):
    # TODO: allow non-self user queries
    user = request.user
    events = [att.event for att in Attendee.objects.filter(user=user, is_attending=True)]
    items = [EventContext(event, user=request.user) for event in events]
    return _render_profile_page(request, user, 'events', {'items': items})


@login_required
def page_user_coupons(request):
    # TODO: allow non-self user queries
    user = request.user
    specials = [coupon.special for coupon in Coupon.objects.filter(user=user, was_used=False)]
    items = [SpecialContext(special, user=request.user) for special in specials]
    return _render_profile_page(request, user, 'specials', {'items': items})
