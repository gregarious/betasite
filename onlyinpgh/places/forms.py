from django import forms

from onlyinpgh.places.models import Place, Location


class PlaceForm(forms.ModelForm):
    class Meta:
        model = Place
        exclude = ('dtcreated',)


class LocationForm(forms.ModelForm):
    class Meta:
        model = Location
