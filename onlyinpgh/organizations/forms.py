from django import forms
from onlyinpgh.organizations.models import Organization


class OrganizationForm(forms.ModelForm):
    '''
    Organization-backed model form. Only exposes organization name.
    '''
    class Meta:
        model = Organization
