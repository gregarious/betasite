from django import forms

from onlyinpgh.feedback.models import GenericFeedbackComment


class GenericFeedbackForm(forms.ModelForm):
    class Meta:
        model = GenericFeedbackComment
        fields = ('feedback',)

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(GenericFeedbackForm, self).__init__(*args, **kwargs)

    def clean(self):
        if not self.user or not self.user.is_authenticated():
            raise forms.ValidationError('User must be logged in to comment.')
        return super(GenericFeedbackForm, self).clean()

    def save(self, commit=True, *args, **kwargs):
        comment = super(GenericFeedbackForm, self).save(commit=False, *args, **kwargs)
        comment.user = self.user
        if commit:
            comment.save()
        return comment
