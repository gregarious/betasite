from django import forms
from django.db import transaction
from django.forms import TextInput
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate
from django.template.defaultfilters import slugify
from django.contrib.auth.models import User

from onlyinpgh.organizations.forms import OrganizationForm
from onlyinpgh.places.forms import PlaceForm, LocationForm
from onlyinpgh.places.models import Location

from onlyinpgh.events.forms import EventForm
from onlyinpgh.specials.forms import SpecialForm

from onlyinpgh.accounts.forms import EmailAuthenticationForm

from onlyinpgh.places.models import Place, Parking, Hours
from onlyinpgh.tags.models import Tag
from onlyinpgh.outsourcing.places import resolve_location
from onlyinpgh.outsourcing.apitools import APIError

from sorl.thumbnail import get_thumbnail
from django.utils.safestring import mark_safe


class ImageWidget(forms.FileInput):
    """
    An ImageField Widget for django.contrib.admin that shows a thumbnailed
    image as well as a link to the current one if it hase one.
    """
    def render(self, name, value, attrs=None):
        output = super(ImageWidget, self).render(name, value, attrs)
        if value and hasattr(value, 'url'):
            try:
                mini = get_thumbnail(value, 'x80', upscale=False)
            except Exception:
                pass
            else:
                output = (
                    u'<div style="float:left">'
                    u'<a style="width:%spx;display:block;margin:0 0 10px" class="thumbnail" target="_blank" href="%s">'
                    u'<img src="%s"></a>%s</div>'
                    ) % (mini.width, value.url, mini.url, output)
        return mark_safe(output)


class SimpleOrgForm(OrganizationForm):
    '''
    Organization-backed model form. Only exposes organization name.
    '''
    class Meta(OrganizationForm.Meta):
        fields = ("name",)


class OrgLoginForm(EmailAuthenticationForm):
    '''
    Form for org admin login. Same as EmailAuthenticationForm now.
    '''
    pass


class OrgAdminPlaceForm(PlaceForm):
    '''
    PlaceForm with the interface to the Location objects simplified
    as a single text address field. All addresses assumed to be in Oakland.

    Internally, the ModelForm-linked location field is declared as an
    excluded field, a non-model linked CharField is declared in it's place.
    All logic is short circuited: see method docs for details.
    '''
    location = forms.CharField(label=u"Address", initial=u'')
    hr_days_1, hr_hours_1 = forms.CharField(initial=u'', required=False), forms.CharField(initial=u'', required=False)
    hr_days_2, hr_hours_2 = forms.CharField(initial=u'', required=False), forms.CharField(initial=u'', required=False)
    hr_days_3, hr_hours_3 = forms.CharField(initial=u'', required=False), forms.CharField(initial=u'', required=False)
    hr_days_4, hr_hours_4 = forms.CharField(initial=u'', required=False), forms.CharField(initial=u'', required=False)
    hr_days_5, hr_hours_5 = forms.CharField(initial=u'', required=False), forms.CharField(initial=u'', required=False)
    hr_days_6, hr_hours_6 = forms.CharField(initial=u'', required=False), forms.CharField(initial=u'', required=False)
    hr_days_7, hr_hours_7 = forms.CharField(initial=u'', required=False), forms.CharField(initial=u'', required=False)
    parking = forms.MultipleChoiceField(choices=Parking.choices, widget=forms.CheckboxSelectMultiple(), required=False)

    tags = forms.CharField(label=u"Tags (comma-separated)", required=False)

    class Meta(PlaceForm.Meta):
        # manually handle the more complex fields
        exclude = ('location', 'tags', 'hours', 'parking')
        widgets = {
            'name': TextInput(attrs={}),
            'image': ImageWidget(),
        }

    def __init__(self, geocode_location=True, *args, **kwargs):
        '''
        Extends base constructor to manually fill in an initial value for
        location when a model instance is given that contains location.name.
        '''
        # if an instance is given, and no initial value for location is given,
        # set the initial value of the location field to the instance's address
        # also set the hours and parking in the roundabout way we do...
        instance = kwargs.get('instance')
        if instance:
            initial = kwargs.setdefault('initial', {})
            if 'location' not in initial and instance.location:
                initial['location'] = instance.location.address

            if 'parking' not in initial:
                # TODO: hackilicious!
                initial['parking'] = instance.parking_as_obj().parking_options

            if 'hours' not in initial:
                day_hrs_tuples = instance.hours_as_obj().day_hours_tuples
                for i in range(1, len(day_hrs_tuples) + 1):
                    days_field, hours_field = 'hr_days_%d' % i, 'hr_hours_%d' % i
                    if days_field not in initial:
                        initial[days_field] = day_hrs_tuples[i - 1][0]
                    if hours_field not in initial:
                        initial[hours_field] = day_hrs_tuples[i - 1][1]

            if 'tags' not in initial:
                initial['tags'] = ', '.join([tag.name for tag in instance.tags.all()])

        self.geocode_location = geocode_location

        super(OrgAdminPlaceForm, self).__init__(*args, **kwargs)

    def clean_tags(self):
        '''
        Parses a string of comma-separated tags and returned a list
        of Tag instances
        '''
        input_names = map(slugify, self.cleaned_data['tags'].split(','))
        # sanitize the input and remove quotations
        input_names = set(name[:50].strip("'").strip('"') for name in input_names if name != '')
        tags = list(Tag.objects.filter(name__in=input_names))
        new_names = input_names.difference([tag.name for tag in tags])
        tags += [Tag(name=tag_name) for tag_name in new_names]
        return tags

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
                return self.instance.location

        # otherwise, we have to create a new location
        location = Location(address=address, postcode='15213',
            town='Pittsburgh', state='PA')

        # if the form is set to geocode new locations
        if self.geocode_location:
            # TODO: make this stuff happen after response is sent, maybe via a signal?
            try:
                resolved = resolve_location(location, retry=0)
                if resolved:
                    location = resolved
            except APIError:
                pass    # do nothing, just go with basic Location

        return location

    @transaction.commit_on_success
    def save(self):
        '''
        Extends the base save by saving the cleaned location entry and
        adding it to the ModelForm's internal place.

        commit=False is not supported. Supporting this may require
        emulating how Django handles defering m2m saving for the tags
        since we're not having hte ModelForm handle them directly.
        '''
        place = super(OrgAdminPlaceForm, self).save(commit=False)

        # process location
        location = self.cleaned_data['location']
        location.save()
        place.location = location

        hours_obj = Hours()
        for i in range(1, 8):
            day = self.cleaned_data.get('hr_days_%d' % i, '')
            hrs = self.cleaned_data.get('hr_hours_%d' % i, '')
            if day or hrs:
                hours_obj.add_span(day, hrs)
        place.set_hours(hours_obj)

        parking_obj = Parking()
        for opt in self.cleaned_data['parking']:
            parking_obj.add_option(opt)
        place.set_parking(parking_obj)

        if place.id is None:
            place.save()    # save if new now so we can add m2m

        # handle tags manually
        new_tags = self.cleaned_data['tags']
        # save all the tags that aren't in the DB yet
        [t.save() for t in new_tags if t.id is None]

        # safe to make a set now, all Tags have a unique ID
        new_tags = set(new_tags)
        # figure out which tags need to be added and removed
        existing_tags = set(place.tags.all())
        # remove all tags that didn't get submitted in the form
        [place.tags.remove(tag_to_rm)
            for tag_to_rm in existing_tags.difference(new_tags)]
        # add all new tags
        [place.tags.add(tag_to_add)
            for tag_to_add in new_tags.difference(existing_tags)]

        place.save()
        return place


class SimplePlaceForm(LocationForm):
    '''
    A Place name + Location form. Actually subclasses LocationForm, easier
    implementation that way.
    '''
    class Meta(LocationForm.Meta):
        exclude = ('latitude', 'longitude', 'country')
        widgets = {'address': forms.TextInput()}

    name = forms.CharField(label=u'Place name', required=False)

    def __init__(self, geocode_location=True, instance=None, *args, **kwargs):
        '''
        Note that instance should be a Place instance, despite the
        subclassing implementation.
        '''
        if instance:
            self.place_instance = instance
            kwargs['instance'] = instance.location
        else:
            self.place_instance = None

        super(SimplePlaceForm, self).__init__(*args, **kwargs)

        self.geocode_location = geocode_location

    @transaction.commit_on_success
    def save(self, commit=False):
        location = super(SimplePlaceForm, self).save(commit=False)

        if self.geocode_location:
            # TODO: make this stuff happen after response is sent, maybe via a signal?
            try:
                resolved = resolve_location(location, retry=0)
                if resolved:
                    location = resolved
            except APIError:
                pass    # do nothing, just go with basic Location

        if commit:
            location.save()

        place = self.place_instance if self.place_instance else Place(location=location)
        place.name = self.cleaned_data.get('name', '')

        if commit:
            place.save()
        return place


class SimpleEventForm(EventForm):
    '''
    Basic event edit form.
    '''
    # TODO: reduce this code. collapse datepicker-start and -end
    # Note that event_edit_form template manually describes these fields!
    dtstart = forms.DateTimeField(
        label=u'Start datetime',
        input_formats=('%m/%d/%Y %I:%M %p', '%m/%d/%Y %I:%M%p',),
        widget=TextInput(attrs={'class': 'datetimepicker-start'}))
    dtend = forms.DateTimeField(
        label=u'End datetime',
        input_formats=('%m/%d/%Y %I:%M %p', '%m/%d/%Y %I:%M%p',),
        widget=TextInput(attrs={'class': 'datetimepicker-end'}))

    # this is a hidden char field becausd we're assuming autocomplete will handle things
    place = forms.CharField(
        label=u'Place',
        widget=forms.HiddenInput(),
        required=False)

    tags = forms.CharField(label=u"Tags (comma-separated)", required=False)

    def __init__(self, *args, **kwargs):
        # first set manual initial values from a given model instance
        instance = kwargs.get('instance')
        initial = kwargs.setdefault('initial', {})
        if instance and 'tags' not in initial:
            initial['tags'] = ', '.join([tag.name for tag in instance.tags.all()])
        super(SimpleEventForm, self).__init__(*args, **kwargs)

    class Meta(EventForm.Meta):
        exclude = ('tags', 'listed')
        widgets = {
            'image': ImageWidget(),

        }

    def clean_place(self):
        pid = self.cleaned_data['place']
        if not pid:
            return None
        try:
            return Place.objects.get(id=pid)
        except Place.DoesNotExist:
            raise forms.ValidationError("Invalid choice")

    def clean_tags(self):
        '''
        Parses a string of comma-separated tags and returned a list
        of Tag instances
        '''
        input_names = map(slugify, self.cleaned_data['tags'].split(','))
        input_names = set(name for name in input_names if name != '')
        tags = list(Tag.objects.filter(name__in=input_names))
        new_names = input_names.difference([tag.name for tag in tags])
        tags += [Tag(name=tag_name) for tag_name in new_names]
        return tags

    @transaction.commit_on_success
    def save(self):
        '''
        commit=False is not supported. Supporting this may require
        emulating how Django handles defering m2m saving for the tags
        since we're not having hte ModelForm handle them directly.
        '''
        event = super(SimpleEventForm, self).save(commit=False)

        if event.place:
            event.place.save()
            event.place = event.place

        if event.id is None:
            event.save()  # save if new now so we can add m2m

        # handle tags manually
        new_tags = set(self.cleaned_data['tags'])
        # save all the tags that aren't in the DB yet
        [t.save() for t in new_tags if t.id is None]

        # figure out which tags need to be added and removed
        existing_tags = set(event.tags.all())
        # remove all tags that didn't get submitted in the form
        [event.tags.remove(tag_to_rm)
            for tag_to_rm in existing_tags.difference(new_tags)]
        # add all new tags
        [event.tags.add(tag_to_add)
            for tag_to_add in new_tags.difference(existing_tags)]

        event.save()
        return event


class SimpleSpecialForm(SpecialForm):
    '''
    Specials edit form with place options limited to the given org's
    establishments
    '''
    # TODO: reduce this code. collapse datepicker-start and -end
    # Note that special_edit_form template manually describes these fields!
    dstart = forms.DateField(
        label=u'Date starts',
        input_formats=('%m/%d/%Y',),
        widget=TextInput(attrs={'class': 'datepicker-start'}),
        required=False)
    dexpires = forms.DateField(
        label=u'Date expires',
        input_formats=('%m/%d/%Y',),
        widget=TextInput(attrs={'class': 'datepicker-end'}),
        required=False)

    tags = forms.CharField(label=u"Tags (comma-separated)", required=False)

    class Meta(SpecialForm.Meta):
        exclude = ('tags', 'points')     # manually handle tags

    def __init__(self, organization, *args, **kwargs):
        '''
        Limit the available places to org's own establishments
        '''
        # first set manual initial values from a given model instance
        instance = kwargs.get('instance')
        initial = kwargs.setdefault('initial', {})
        if instance and 'tags' not in initial:
            initial['tags'] = ', '.join([tag.name for tag in instance.tags.all()])

        place_choices = organization.establishments.all()
        if 'place' not in initial and (not instance or not instance.place):
            if place_choices.count() == 1:
                initial['place'] = place_choices[0]

        super(SimpleSpecialForm, self).__init__(*args, **kwargs)
        self.fields['place'].queryset = place_choices

    def clean_tags(self):
        '''
        Parses a string of comma-separated tags and returned a list
        of Tag instances
        '''
        input_names = map(slugify, self.cleaned_data['tags'].split(','))
        input_names = set(name for name in input_names if name != '')
        tags = list(Tag.objects.filter(name__in=input_names))
        new_names = input_names.difference([tag.name for tag in tags])
        tags += [Tag(name=tag_name) for tag_name in new_names]
        return tags

    @transaction.commit_on_success
    def save(self):
        '''
        commit=False is not supported. Supporting this may require
        emulating how Django handles defering m2m saving for the tags
        since we're not having hte ModelForm handle them directly.
        '''
        special = super(SimpleSpecialForm, self).save(commit=False)

        special.place.save()
        special.place = special.place
        if special.id is None:
            special.save()  # save if new now so we can add m2m

        # handle tags manually
        new_tags = set(self.cleaned_data['tags'])
        # save all the tags that aren't in the DB yet
        [t.save() for t in new_tags if t.id is None]

        # figure out which tags need to be added and removed
        existing_tags = set(special.tags.all())
        # remove all tags that didn't get submitted in the form
        [special.tags.remove(tag_to_rm)
            for tag_to_rm in existing_tags.difference(new_tags)]
        # add all new tags
        [special.tags.add(tag_to_add)
            for tag_to_add in new_tags.difference(existing_tags)]

        special.save()
        return special


class PlaceClaimForm(forms.Form):
    '''
    Form with just a place choice input.

    Will default to using a select widget for the field, but practically,
    an Autocomplete field should be used. Currently, this requires some
    manual configuration in the form template.
    '''
    place = forms.ChoiceField(label='Place name')

    def __init__(self, place_choices, *args, **kwargs):
        super(PlaceClaimForm, self).__init__(*args, **kwargs)
        self.fields['place'].choices = [(p.id, p.name) for p in place_choices]
