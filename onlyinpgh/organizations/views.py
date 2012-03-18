from django.http import HttpResponse, HttpResponseServerError
from django.shortcuts import render, redirect
from django.utils.safestring import mark_safe

from django.template import RequestContext
from django.template.loader import render_to_string

from onlyinpgh.places.models import Place
from onlyinpgh.organizations.models import Organization
from onlyinpgh.organizations.forms import OrgUserCreationForm
from django.contrib.auth import authenticate, login, logout


from onlyinpgh.accounts.models import FakeUser

def biz_signup(request):
    logout(request)

    if request.POST:
        form = OrgUserCreationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password2']
            business = form.cleaned_data['business']

            seminar_admin = authenticate(username='seminar', password='seminar')
            if not seminar_admin:
                return HttpResponseServerError("Failure code 58008")
            else:
                login(request, seminar_admin)

            # just looking up place by name now. no id returned from autocomplete field
            place, _ = Place.objects.get_or_create(name=business)

            org = Organization.objects.create(name=place.name)
            org.administrators.add(seminar_admin)
            org.establishments.add(place)

            fake = FakeUser.objects.create(username=email, password=password, org=org, place=place)
            request.session['fakeuser'] = fake

            print 'set the session. redirecting'
            return redirect('biz_admin_home')
    else:
        form = OrgUserCreationForm()

    form_html = mark_safe(render_to_string(
        'organizations/manage/signup.html', {'form': form},
        context_instance=RequestContext(request)))
    return render(request, 'manage_base.html', {'content': form_html})


def biz_admin_home(request):
    if 'fakeuser' not in request.session:
        return redirect('biz_signup')
    content = mark_safe(render_to_string(
        'organizations/manage/home.html', {},
        context_instance=RequestContext(request)))


    print 'in biz admin as ' + str(request.session['fakeuser'])
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
