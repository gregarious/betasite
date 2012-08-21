from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import render_to_response, get_object_or_404
from django.core.urlresolvers import reverse

from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm

from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect

from scenable.accounts.forms import EmailAuthenticationForm, BetaRegistrationForm, \
        UserProfileForm, ActivityPreferencesForm, EmailForm, RememberMeForm
from scenable.common.views import PageContext

import urlparse

from scenable.places.models import Favorite
from scenable.places.viewmodels import PlaceData

from scenable.events.models import Attendee
from scenable.events.viewmodels import EventData

from scenable.specials.models import Coupon
from scenable.specials.viewmodels import SpecialData


def login(request, *args, **kwargs):
    '''
    Wrapper around auth's login to support persistant login via a
    "Remember me?" POST value.
    '''
    if not request.POST.get('remember_me', None):
        request.session.set_expiry(0)
    return auth_login(request, *args, **kwargs)


@csrf_protect
@never_cache
def page_login(request, redirect_field_name='next'):
    '''
    Renders login page.
    '''
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('beta-home'))

    redirect_to = request.REQUEST.get(redirect_field_name, '')
    if request.method == "POST":
        form = EmailAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            netloc = urlparse.urlparse(redirect_to)[1]

            # Use default setting if redirect_to is empty
            if not redirect_to:
                redirect_to = reverse('beta-home')

            # Security check -- don't allow redirection to a different
            # host.
            elif netloc and netloc != request.get_host():
                redirect_to = reverse('beta-home')

            # Okay, security checks complete. Log the user in.
            login(request, form.get_user())
            RememberMeForm

            if request.session.test_cookie_worked():
                request.session.delete_test_cookie()

            return HttpResponseRedirect(redirect_to)
    else:
        form = EmailAuthenticationForm(request)
    request.session.set_test_cookie()

    content = dict(
        form=form,
        form_action=reverse('login'),
        remember_me=RememberMeForm(),
        next=redirect_to
    )
    context = PageContext(request,
        page_title='Scenable | Login',
        content_dict=content)
    return render_to_response('registration/page_login.html', context_instance=context)


def page_signup(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('beta-home'))

    # if POST request, handle the form submission
    if request.POST:
        reg_form = BetaRegistrationForm(data=request.POST, prefix='reg')
        profile_form = UserProfileForm(data=request.POST, prefix='prof')

        if reg_form.is_valid() and profile_form.is_valid():
            print 'yo', reg_form.cleaned_data
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
                redirect_to = reverse('beta-home')
            else:   # if cookies aren't enabled, go to login page
                redirect_to = reverse('login')

            return HttpResponseRedirect(redirect_to)
    else:
        reg_form = BetaRegistrationForm(prefix='reg')
        profile_form = UserProfileForm(prefix='prof')

    request.session.set_test_cookie()

    content = dict(
        registration_form=reg_form,
        profile_form=profile_form,
        remember_me=RememberMeForm(),
        form_action=reverse('signup')
    )
    context = PageContext(request,
        page_title='Scenable | Sign Up',
        content_dict=content)
    return render_to_response('registration/page_signup.html', context_instance=context)


def _render_profile_page(request, public_user, current_panel=None, variables={}):
    variables['public_user'] = public_user
    variables['current_panel'] = current_panel
    context = PageContext(request,
        current_section='accounts',
        page_title='Scenable | %s\'s Profile' % public_user.username,
        content_dict=variables)
    return render_to_response('accounts/page_profile.html', context_instance=context)


def page_public_account(request, uname):
    '''
    If uname refers to the current user's account, redirects to the account
    management panel. Otherwise just shows the public profile.
    '''
    user = get_object_or_404(User, username=uname)
    # if the profile requested is the current user's, redirect to manage
    if user == request.user:
        return HttpResponseRedirect(reverse('account-manage', kwargs={'uname': uname}))
    else:
        return _render_profile_page(request, user, None)


#@login_required
def page_manage_account(request, uname):
    '''
    Main profile page view function, all panels are generated through here.
    - user is the User whose profile is being generated
    - current_panel is an enum string with on of the following values:
        account, places, events, specials.
    '''
    print request.POST
    forms_saved = []
    # only allow access to the page if the current user matches the url
    user = get_object_or_404(User, username=uname)
    if user != request.user:
        return HttpResponseForbidden()

    # 4 separate instances of the standard form building/saving pattern,
    # controlled primarily by which submit button was clicked
    if 'save_profile' in request.POST:
        profile_form = UserProfileForm(data=request.POST, files=request.FILES,
            instance=user.get_profile())
        if profile_form.is_valid():
            profile_form.save()
            forms_saved.append(profile_form)
    else:
        profile_form = UserProfileForm(instance=user.get_profile())

    if 'save_preferences' in request.POST:
        preferences_form = ActivityPreferencesForm(data=request.POST,
            instance=user.get_profile())
        if preferences_form.is_valid():
            preferences_form.save()
            forms_saved.append(preferences_form)
    else:
        preferences_form = ActivityPreferencesForm(instance=user.get_profile())

    if 'save_email' in request.POST:
        email_form = EmailForm(instance=user, data=request.POST)
        if email_form.is_valid():
            email_form.save()
            forms_saved.append(email_form)
    else:
        email_form = EmailForm(instance=user)

    if 'save_password' in request.POST:
        password_form = PasswordChangeForm(user=user, data=request.POST)
        if password_form.is_valid():
            password_form.save()
            forms_saved.append(password_form)
    else:
        password_form = PasswordChangeForm(user=user)

    forms = dict(
        profile_form=profile_form,
        password_form=password_form,
        email_form=email_form,
        preferences_form=preferences_form)
    return _render_profile_page(request, user, 'account',
        {'account_forms': forms, 'forms_saved': forms_saved})


def page_user_favorites(request, uname):
    user = get_object_or_404(User, username=uname)
    # hide favorites if privacy settings dictate
    if user != request.user and not user.get_profile().public_favorites:
        items = []
    else:
        places = [fav.place for fav in Favorite.objects.filter(user=user)]
        items = [PlaceData(place, user=request.user) for place in places]
    return _render_profile_page(request, user, 'places', {'feed_items': items})


def page_user_attendance(request, uname):
    user = get_object_or_404(User, username=uname)
    # hide attendance if privacy settings dictate
    if user != request.user and not user.get_profile().public_attendance:
        items = []
    else:
        events = [att.event for att in Attendee.objects.filter(user=user)]
        items = [EventData(event, user=request.user) for event in events]
    return _render_profile_page(request, user, 'events', {'feed_items': items})


def page_user_coupons(request, uname):
    user = get_object_or_404(User, username=uname)
    # hide coupons if privacy settings dictate
    if user != request.user and not user.get_profile().public_coupons:
        items = []
    else:
        specials = [coupon.special for coupon in Coupon.objects.filter(user=user, was_used=False)]
        items = [SpecialData(special, user=request.user) for special in specials]
    return _render_profile_page(request, user, 'specials', {'feed_items': items})
