from django.http import HttpResponse
from django.shortcuts import render
from django.utils.safestring import mark_safe

from django.template import RequestContext
from django.template.loader import render_to_string


from onlyinpgh.organizations.forms import OrgUserCreationForm


def biz_signup(request):
    if request.POST:
        form = OrgUserCreationForm(request.POST)
        if form.is_valid():
            user, org, place = form.complete_registration()
            print 'created!'
            print user
            print org
            print place
    else:
        form = OrgUserCreationForm()

    form_html = mark_safe(render_to_string(
        'organizations/manage/signup.html', {'form': form},
        context_instance=RequestContext(request)))
    return render(request, 'manage_base.html', {'content': form_html})

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
