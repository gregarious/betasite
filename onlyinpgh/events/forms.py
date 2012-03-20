from django import forms

from onlyinpgh.events.models import Event


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        exclude = ('dtcreated', 'dtmodified',)
