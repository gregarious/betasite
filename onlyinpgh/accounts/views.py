from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.template import RequestContext
from django.template.loader import render_to_string
from onlyinpgh.accounts.forms import RegistrationForm, UserProfileForm

from django.core.urlresolvers import reverse
from django.contrib.auth import login, authenticate


# TODO: create this view once there's some time. default django view is ok,
# but it doesn't test for cookies, is kind of awkward to use with our
# module-based page building, etc.
def page_login(request):
    pass


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
    context = RequestContext(request)
    content = render_to_string('registration/signup_form.html',
        {'registration_form': reg_form, 'profile_form': profile_form,
         'form_action': reverse('login')},
        context_instance=context)

    return render(request, 'page.html', {'main_content': content})
