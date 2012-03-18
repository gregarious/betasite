from django.template import render
from django.template.loaders import get_template
from django.template.defaultfilters import slugify

from django.contrib.auth.models import create_user
from onlyinpgh.places.models import Place
from onlyinpgh.places.views import get_create_place_wizard

import re

# def signup(request):
#     # if POST request, handle the form submission
#     if request.POST:
#         form_errors = 
#         username = slugify(request.POST['place_name'])
#         user = create_user(username, email=request.POST['email'],
#             password=)
#         # create a new user with an automatically generated username
#         # (slugified with random suffix if necessary)

#         # create a new organization with name = POST.place_name
#         # set new user as administrator
#         # save the organization id in the user's session vbl

#         # goto create_place with pid or place_name
#         pass

#     return render(request, 'manage_base.html',
#         {'content': signup_form})


# TEMPORARY: used if something bad happens between signup and place creation
def login(request):
    # if POST request, handle the form submission
    if request.POST:
        # if user has no organizations, create one the same was as in signup, set admin, session
        # elif user has > 1 org, set session to first one

        # if org has no places attached, goto create_place()
        # else: go to home
        pass


def create_place(request, pid=None, pname=None):
    # if POST request, handle the form submission
    if request.POST:
        # ensure the Org has the right to edit the place if an ID is given!!!!!!!!
        place.save()

    # serve up the place creation wizard
    # autofill the place if a pid or place name were given
    if pid:
        try:
            place = Place.objects.create(pid=pid)
        except Place.DoesNotExist:
            place = Place(name=pname)
    else:
        place = Place(name=pname)

    creation_form = get_create_place_wizard(place=place)

    return render(request, 'manage_base.html',
        {'content': creation_form})


def management_home(request):
    home_page = get_template('organizations/manage/home.html')
    return render(request, home_page,
        {'content': home_page})