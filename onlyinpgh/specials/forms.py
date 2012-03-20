from django import forms

from onlyinpgh.specials.models import Special


class SpecialForm(forms.ModelForm):
    class Meta:
        model = Special
