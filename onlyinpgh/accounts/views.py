from django.http import HttpResponseRedirect
from django.template import RequestContext

from django.core.urlresolvers import reverse

from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required

from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect

from onlyinpgh.common.core.rendering import render_viewmodel, render_safe
from onlyinpgh.accounts.forms import RegistrationForm, UserProfileForm
from onlyinpgh.common.views import page_response, render_main
import urlparse

from onlyinpgh.accounts.viewmodels import PublicProfile

from onlyinpgh.places.models import Favorite
from onlyinpgh.places.viewmodels import PlaceFeedItem

from onlyinpgh.events.models import Attendee
from onlyinpgh.events.viewmodels import EventFeedItem

from onlyinpgh.specials.models import Coupon
from onlyinpgh.specials.viewmodels import SpecialFeedItem


@csrf_protect
@never_cache
def page_login(request, redirect_field_name='next'):
    '''
    Renders login page.
    '''
    redirect_to = request.REQUEST.get(redirect_field_name, '')
    print 'redir:', redirect_to
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

    # render login form with csrf protection
    login_form = render_safe('registration/login.html',
        form=form, form_action=reverse('login'),
        next=redirect_to,
        context_instance=RequestContext(request))
    main_content = render_main(login_form, include_scenenav=True)
    return page_response(main_content, request)


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
    content = render_safe('registration/signup.html',
        registration_form=reg_form,
        profile_form=profile_form,
        form_action=reverse('signup'),
        context_instance=RequestContext(request))
    return page_response(content, request)


def render_account_panel(panel_content, wrap_main=True):
    '''
    Returns a rendered account panel, suitable for direct use in a
    page_response call if wrap_main is True.
    '''
    panel = render_safe('accounts/account_panel.html', panel_content=panel_content)
    return render_main(panel, include_scenenav=True) if wrap_main else panel


@login_required
def page_profile(request):
    profile = render_viewmodel(PublicProfile(request.user), 'accounts/public_profile.html')
    main = render_account_panel(profile)
    return page_response(main, request)


@login_required
def page_my_places(request):
    places = [fav.place for fav in Favorite.objects.filter(user=request.user, is_favorite=True)]
    items = [PlaceFeedItem(place, user=request.user) for place in places]

    rendered_items = [render_viewmodel(item, 'places/feed_item.html') for item in items]
    main = render_account_panel(
        render_safe('accounts/my_places.html', items=rendered_items))
    return page_response(main, request)


@login_required
def page_my_events(request):
    events = [att.event for att in Attendee.objects.filter(user=request.user, is_attending=True)]
    items = [EventFeedItem(event, user=request.user) for event in events]

    rendered_items = [render_viewmodel(item, 'events/feed_item.html') for item in items]
    main = render_account_panel(
        render_safe('accounts/my_events.html', items=rendered_items))
    return page_response(main, request)


@login_required
def page_my_specials(request):
    specials = [coupon.special for coupon in Coupon.objects.filter(user=request.user, was_used=False)]
    items = [SpecialFeedItem(special, user=request.user) for special in specials]

    rendered_items = [render_viewmodel(item, 'specials/feed_item.html') for item in items]
    main = render_account_panel(
        render_safe('accounts/my_specials.html', items=rendered_items))
    return page_response(main, request)
