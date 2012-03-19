from django import forms
from django.contrib.auth.models import User
from onlyinpgh.places.models import Place
from onlyinpgh.organizations.models import Organization


class OrgUserCreationForm(forms.Form):
    """
    Form for org signups in the social media seminar business.

    Code modeled off of django.contrib.auth.forms.UserCreationForm.

    Form creates a User from the email and password. Also offers methods
    that create the initial Organization this user will have authorization
    over, and link that Org to a default Place (either existing or new).
    """
    email = forms.EmailField(label="Email address", initial='')
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Password confirmation", widget=forms.PasswordInput)

    # TODO: make this a AutoComplete field. All autocomplete stuff is hardcoded into form template right now.
    business = forms.CharField(label="Business name", initial='', required=True)

    def clean_email(self):
        email = self.cleaned_data["email"]
        try:
            User.objects.get(email=email)
        except User.DoesNotExist:
            return email
        raise forms.ValidationError("A user with that email address already exists.")

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1", "")
        password2 = self.cleaned_data["password2"]
        if password1 != password2:
            raise forms.ValidationError("The two password fields didn't match.")
        return password2

    # def clean_business(self):
    #     '''
    #     Business name will either be a business id string, or an "!name".
    #     When cleaning, transform it to a Place object.
    #     '''
    #     business = self.cleaned_data["business"].strip()
    #     if not business:
    #         raise forms.ValidationError("A business name must be provided.")

    #     if business.startswith('!'):
    #         place = Place(name=business[1:])
    #     else:
    #         try:
    #             place = Place.objects.get(id=int(business))
    #         except Place.DoesNotExist:
    #             raise forms.ValidationError("Error retreiving autocompleted business name.")
    #     return place


    # def complete_registration(self):
    #     '''
    #     Saves the the new user, new org, and new/existing business. Also
    #     returns them as a 3-tuple.
    #     '''
    #     print 'in complete'
    #     if not self.is_valid():
    #         raise Exception("Cannot register with in invalid form.")

    #     # clean_business turned the given business name into a Place
    #     business = self.cleaned_data["business"].strip()
    #     email = self.cleaned_data["email"].strip()
    #     password = self.cleaned_data["password1"]

    #     # just set username as email now
    #     username = email
    #     try:
    #         User.objects.get(username=username)
    #     except User.DoesNotExist:
    #         try:
    #             user = User.objects.create_user(username=username, email=email, password=password)
    #         except IntegrityError:
    #             pass
    #     else:
    #         raise Exception('User already exists!')

    #     # just looking up place by name now. no id returned from autocomplete field
    #     place = Place.objects.get_or_create(name=business)

    #     org = Organization.objects.create(name=place.name)
    #     org.administrators.add(user)
    #     org.establishments.add(place)

    #     return user, org, place


class PlaceClaimForm(forms.Form):
    """
    Form for org signups in the social media seminar business.

    Code modeled off of django.contrib.auth.forms.UserCreationForm.

    Form creates a User from the email and password. Also offers methods
    that create the initial Organization this user will have authorization
    over, and link that Org to a default Place (either existing or new).
    """
    email = forms.EmailField(initial='')
    password1 = forms.CharField(widget=forms.PasswordInput)

    business = forms.CharField(label="Business name", initial='', required=True)

    def complete_registration(self):
        '''
        Saves the the new user, new org, and new/existing business. Also
        returns them as a 3-tuple.
        '''
        print 'in complete'
        if not self.is_valid():
            raise Exception("Cannot register with an invalid form.")

        email = self.cleaned_data["email"].strip()
        password = self.cleaned_data["password1"]

        user = authenticate(username='john', password='secret')

        user = User.objects.get(username=self.email)
        # clean_business turned the given business name into a Place
        business = self.cleaned_data["business"].strip()
        email = self.cleaned_data["email"].strip()
        password = self.cleaned_data["password1"]

        # just set username as email now
        username = email
        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            try:
                user = User.objects.create_user(username=username, email=email, password=password)
            except IntegrityError:
                pass
        else:
            raise Exception('User already exists!')

        # just looking up place by name now. no id returned from autocomplete field
        place = Place.objects.get_or_create(name=business)

        org = Organization.objects.create(name=place.name)
        org.administrators.add(user)
        org.establishments.add(place)

        return user, org, place

