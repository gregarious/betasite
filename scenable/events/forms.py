from django import forms

from scenable.events.models import Event


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        exclude = ('dtcreated', 'dtmodified',)
