from django import forms

from scenable.specials.models import Special


class SpecialForm(forms.ModelForm):
    class Meta:
        model = Special
