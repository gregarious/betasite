from django.http import HttpResponse, HttpResponseServerError
from django.shortcuts import render, redirect
from django.utils.safestring import mark_safe

from django.template import RequestContext
from django.template.loader import render_to_string

from onlyinpgh.places.models import Place
from onlyinpgh.organizations.models import Organization
from onlyinpgh.organizations.forms import OrgUserCreationForm, PlaceClaimForm
from django.contrib.auth import authenticate, login

from django.db import IntegrityError


def biz_signup(request):
    if request.POST:
        form = OrgUserCreationForm(request.POST)
        if form.is_valid():
            # user, org, place = form.complete_registration()
            email = form.cleaned_data["email"].strip()
            password = form.cleaned_data["password1"]

            # just set username as email now
            username = email
            try:
                User.objects.get(username=username)
            except User.DoesNotExist:
                try:
                    User.objects.create_user(username=username, email=email, password=password)
                except IntegrityError:
                    print 'hacked together new user',username
                    return place_claim(request)
            else:
                return HttpResponseServerError('Internal server error. At least I prepared this error message for you, dear user. Code 1.')
    else:
        form = OrgUserCreationForm()

    form_html = mark_safe(render_to_string(
        'organizations/manage/signup.html', {'form': form},
        context_instance=RequestContext(request)))
    return render(request, 'manage_base.html', {'content': form_html})


def place_claim(request):
    if request.POST:
        form = PlaceClaimForm(request.POST)
        # if form.is_valid():
        #     email = form.cleaned_data["email"].strip()
        #     password = form.cleaned_data["password1"]
        #     business = form.cleaned_data["business"]

        #     user = authenticate(username=email, password=password)
        #     if user is not None:
        #         print 'logging in', user
        #         login(request, user)
        #     else:
        #         return HttpResponseServerError('Internal server error. At least I prepared this error message for you, dear user. Code 2.')

        #     # just looking up place by name now. no id returned from autocomplete field
        #     place, _ = Place.objects.get_or_create(name=business)

        #     org = Organization.objects.create(name=place.name)
        #     org.administrators.add(user)
        #     org.establishments.add(place)

        #     request.session['working_place'] = place
        #     request.session['working_org'] = org
        #     print 'set the session. redirecting'
        #     return redirect('biz_admin_home')
    else:
        form = PlaceClaimForm()

    form_html = mark_safe(render_to_string(
        'organizations/manage/claim_biz.html', {'form': form},
        context_instance=RequestContext(request)))
    return render(request, 'manage_base.html', {'content': form_html})


def biz_admin_home(request):
    content = mark_safe(render_to_string(
        'organizations/manage/home.html', {},
        context_instance=RequestContext))

    return render(request, 'manage_base.html', {'content': content})

### TESTING ####
from django.contrib.auth.models import User


def createone(username):
    print 'starting test'
    print 'current users:'
    for u in User.objects.all():
        print '  id', u.id
        print '  name', u.username
        print '  email', u.email

    password = 'password'
    email = 'newguy@something.com'
    print 'attempting to add', username

    User.objects.create_user(
        username=username,
        email=email,
        password=password
    )

    print 'worked!'


def usercreation_test(request):
    print 'from the view:'
    createone('serveruser')
    return HttpResponse('worked!')
