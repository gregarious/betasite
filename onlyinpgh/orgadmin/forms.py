from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

from onlyinpgh.places.forms import PlaceForm
from onlyinpgh.places.models import Location

from onlyinpgh.events.forms import EventForm
from onlyinpgh.specials.forms import SpecialForm

from onlyinpgh.outsourcing.places import resolve_location
from onlyinpgh.outsourcing.apitools import APIError


class OrgSignupForm(UserCreationForm):
    '''
    Form for org signups in the org admin panel. Similar to a UserCreationForm
    but with an additional organization name input.

    Currently assumes email address is username.
    '''
    # override the default username field as an email address. this is how business
    # signups will be handled for now
    username = forms.EmailField(label="Email address", initial='', max_length=30, required=True)
    orgname = forms.CharField(label="Organization", initial='', required=True)

    def clean_username(self):
        '''
        Overridden to rephrase username validation error
        '''
        try:
            cleaned = super(OrgSignupForm, self).clean_username()
            print 'returned as ', cleaned
        except forms.ValidationError:
            # rephrase the validation error
            raise forms.ValidationError("An organization with that email already exists.")
        else:
            return cleaned

    def save(self, commit=True):
        '''
        Override of User ModelForm that saves the email address as well as
        username and password.
        '''
        user = super(OrgSignupForm, self).save(commit=False)
        user.email = self.cleaned_data['username']
        if commit:
            user.save()
        return user


class OrgLoginForm(AuthenticationForm):
    '''
    Form for org admin login.

    Currently assumes email address is username.
    '''
    username = forms.CharField(label="Email address", initial='')


class SimpleLocationPlaceForm(PlaceForm):
    '''
    PlaceForm with the interface to the Location objects simplified
    as a single text address field. All addresses assumed to be in Oakland.

    Internally, the ModelForm-linked location field is declared as an
    excluded field, a non-model linked CharField is declared in it's place.
    All logic is short circuited: see method docs for details.
    '''
    location = forms.CharField(label="Address", initial='')

    class Meta(PlaceForm.Meta):
        # TODO: look into extending from parent meta
        exclude = ('dtcreated', 'location', 'tags',)

    def __init__(self, geocode_locations=True, *args, **kwargs):
        '''
        Extends base constructor to manually fill in an initial value for
        location when a model instance is given that contains location.name.
        '''
        # if an instance is given, and no initial value for location is given,
        # set the initial value of the location field to the instance's address
        instance = kwargs.get('instance')
        if instance and instance.location:
            initial = kwargs.setdefault('initial', {})
            if 'location' not in initial:
                initial['location'] = instance.location.address

        self.geocode_locations = geocode_locations

        super(SimpleLocationPlaceForm, self).__init__(*args, **kwargs)

    def clean_location(self):
        '''
        If the text-based location is a new address for the ModelForm's
        internal  place instance, turn it into a true Location. Otherwise,
        return the stored instance's location.
        '''
        address = self.cleaned_data['location'].strip()

        # if there's already a location stored in this form's instance, just return it assuming the field hasn't changed
        if self.instance.location:
            if self.instance.location.address.strip() == address:
                print 'address unchanged'
                return self.instance.location

        # otherwise, we have to create a new location
        location = Location(address=address, postcode='15213',
            town='Pittsburgh', state='PA')

        # if the form is set to geocode new locations
        if self.geocode_locations:
            # TODO: make this stuff happen after response is sent, maybe via a signal?
            try:
                print 'attempting resolve'
                resolved = resolve_location(location, retry=0)
                if resolved:
                    print 'new one resolved!', resolved.longitude, resolved.latitude
                    location = resolved
            except APIError:
                pass    # do nothing, just go with basic Location

        return location

    def save(self, commit=True):
        '''
        Extends the base save by saving the cleaned location entry and
        adding it to the ModelForm's internal place.
        '''
        place = super(SimpleLocationPlaceForm, self).save(commit=False)

        location = self.cleaned_data['location']
        if commit:
            location.save()

        place.location = location
        if commit:
            place.save()
            print 'saved place id', place.id
        return place


class SimpleEventForm(EventForm):
    '''
    Event edit form with place options limited to the given org's
    establishments
    '''
    class Meta(EventForm.Meta):
        # TODO: look into extending from parent meta
        exclude = ('dtcreated', 'dtmodified', 'tags', )

    def __init__(self, organization, *args, **kwargs):
        '''
        Limit the available places to org's own establishments
        '''
        super(SimpleEventForm, self).__init__(*args, **kwargs)
        self.fields['place'].queryset = organization.establishments.all()


class SimpleSpecialForm(SpecialForm):
    '''
    Specials edit form with place options limited to the given org's
    establishments
    '''
    class Meta(SpecialForm.Meta):
        # TODO: look into extending from parent meta
        exclude = ('tags',)

    def __init__(self, organization, *args, **kwargs):
        '''
        Limit the available places to org's own establishments
        '''
        super(SimpleSpecialForm, self).__init__(*args, **kwargs)
        self.fields['place'].queryset = organization.establishments.all()


class PlaceClaimForm(forms.Form):
    place = forms.ChoiceField(label='Places')

    def __init__(self, place_choices, *args, **kwargs):
        super(PlaceClaimForm, self).__init__(*args, **kwargs)
        self.fields['place'].choices = [(p.id, p.name) for p in place_choices]
