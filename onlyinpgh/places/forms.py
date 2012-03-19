from django import forms
from onlyinpgh.places.models import Place


class PlaceForm(forms.ModelForm):
    class Meta:
        model = Place
        exclude = ('dtcreated',)
