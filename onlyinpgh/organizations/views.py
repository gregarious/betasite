from django.shortcuts import render

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

    return render(request, 'organizations/manage/signup.html', {'form': form})
