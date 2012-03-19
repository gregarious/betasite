from django.http import HttpResponse, HttpResponseRedirect
from django.template.loader import render_to_string
from django.template import RequestContext
from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse
from django.forms.util import ErrorList
from django.contrib.auth import login, authenticate, logout

from onlyinpgh.orgadmin.forms import OrgSignupForm, OrgLoginForm
from onlyinpgh.organizations.models import Organization


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
            request.session['current_org'] = Organization.objects.filter(administrators=user)[0]

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


def page_home(request):
    # must be authenticated to reach this page
    if not request.user.is_authenticated():
        return HttpResponseRedirect(reverse('orgadmin-login'))

    context = RequestContext(request,
        {'current_org': request.session['current_org']})
    content = render_to_string('orgadmin/home.html', context_instance=context)
    return response_admin_page(content, context)


def page_claim_place(request):
    # must be authenticated to reach this page
    if not request.user.is_authenticated():
        return HttpResponseRedirect(reverse('orgadmin-login'))

    context = RequestContext(request,
        {'current_org': request.session['current_org']})
    content = render_to_string('orgadmin/place_claim.html', context_instance=context)
    return response_admin_page(content, context)


def page_setup_place_wizard(request):
    # must be authenticated to reach this page
    if not request.user.is_authenticated():
        return HttpResponseRedirect(reverse('orgadmin-login'))

    context = RequestContext(request,
        {'current_org': request.session['current_org']})
    content = render_to_string('orgadmin/place_setup_wizard.html', context_instance=context)
    return response_admin_page(content, context)


def page_edit_place(request, id):
    # must be authenticated to reach this page
    if not request.user.is_authenticated():
        return HttpResponseRedirect(reverse('orgadmin-login'))

    context = RequestContext(request,
        {'current_org': request.session['current_org']})
    content = render_to_string('orgadmin/place_edit_form.html', context_instance=context)
    return response_admin_page(content, context)


def page_list_places(request):
    # must be authenticated to reach this page
    if not request.user.is_authenticated():
        return HttpResponseRedirect(reverse('orgadmin-login'))

    context = RequestContext(request,
        {'current_org': request.session['current_org']})
    content = render_to_string('orgadmin/place_list.html', context_instance=context)
    return response_admin_page(content, context)


def page_edit_event(request, id):
    # must be authenticated to reach this page
    if not request.user.is_authenticated():
        return HttpResponseRedirect(reverse('orgadmin-login'))

    context = RequestContext(request,
        {'current_org': request.session['current_org']})
    content = render_to_string('orgadmin/event_edit_form.html', context_instance=context)
    return response_admin_page(content, context)


def page_list_events(request):
    # must be authenticated to reach this page
    if not request.user.is_authenticated():
        return HttpResponseRedirect(reverse('orgadmin-login'))

    context = RequestContext(request,
        {'current_org': request.session['current_org']})
    content = render_to_string('orgadmin/event_list.html', context_instance=context)
    return response_admin_page(content, context)


def page_edit_special(request, id):
    # must be authenticated to reach this page
    if not request.user.is_authenticated():
        return HttpResponseRedirect(reverse('orgadmin-login'))

    context = RequestContext(request,
        {'current_org': request.session['current_org']})
    content = render_to_string('orgadmin/special_edit_form.html', context_instance=context)
    return response_admin_page(content, context)


def page_list_specials(request):
    # must be authenticated to reach this page
    if not request.user.is_authenticated():
        return HttpResponseRedirect(reverse('orgadmin-login'))

    context = RequestContext(request,
        {'current_org': request.session['current_org']})
    content = render_to_string('orgadmin/special_list.html', context_instance=context)
    return response_admin_page(content, context)
